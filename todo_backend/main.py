from flask import Flask, request, redirect, jsonify
import os
import logging
import psycopg2
import json
from nats import connect

POSTGRES_URL = os.environ.get('POSTGRES_URL', 
                              'postgresql://postgres@localhost/postgres')
NATS_URL = os.environ.get('NATS_URL', 
                          'nats://localhost:4222')

class TodoBackend:
    def __init__(self):        
        self.port = int(os.environ.get('PORT', 5005))
        self.flask_app = Flask(__name__)
        self.setup_routes()
        
        self.db_conn = None
        
    def init_db(self):
        try:
            conn = psycopg2.connect(POSTGRES_URL)
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS todos (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        done BOOLEAN NOT NULL DEFAULT FALSE
                    );
                """)
                conn.commit()
        except Exception as e:
            self.flask_app.logger.error(f"Failed to connect to DB at {POSTGRES_URL}: {e}")

        self.db_conn = conn

    def add_todo(self, name):
        with self.db_conn.cursor() as cur:
            cur.execute("INSERT INTO todos (name, done) VALUES (%s, FALSE) RETURNING id;", (name,))
            self.db_conn.commit()
            return cur.fetchone()[0] # type: ignore

    def mark_done(self, id):
        with self.db_conn.cursor() as cur:
            cur.execute(
                "UPDATE todos SET done = TRUE WHERE id = %s RETURNING done",
                (id,)
            )
            result = cur.fetchone()
            self.db_conn.commit()

            return result[0] if result else None

    def get_todos(self):
        with self.db_conn.cursor() as cur:
            cur.execute("SELECT id, name, done FROM todos ORDER BY id;")
            rows = cur.fetchall()
            return [{"id": r[0], "name": r[1], "done": r[2]} for r in rows]

    def setup_routes(self):
        @self.flask_app.route("/")
        def root():
            return "OK", 200
        
        @self.flask_app.route("/healthz")
        def ready():
            if self.db_conn is None:
                self.db_conn = self.init_db()

            if self.db_conn is not None:
                return "OK", 200
            else:
                return "Service unavailable", 503

        @self.flask_app.route('/todos', methods=['GET', 'POST'])
        async def todo():
            if self.db_conn is None:
                self.db_conn = self.init_db()

            if request.method == 'POST':
                todo_text = request.form.get('todo')
                if not todo_text and request.is_json and request.json is not None:
                    todo_text = request.json.get('todo')

                if not todo_text:
                    self.flask_app.logger.warning("Missing todo text in request")
                    return jsonify({"error": "Missing todo"}), 400

                if len(todo_text) > 140:
                    self.flask_app.logger.warning(f"Failed to add todo item {repr(todo_text)}. \
                                                  Length exceeds limit of 140 characters")
                    return jsonify({"error": "Todo must be 140 characters or less"}), 400

                todo_id = self.add_todo(todo_text)
                self.flask_app.logger.info(f"Added todo item {repr(todo_text)} with id {todo_id}")
                
                msg = json.dumps({"id": todo_id, "operation": "created"})
                await nats_send(msg)
                
                return redirect("/")
            elif request.method == 'GET':
                return jsonify({"todos": self.get_todos()})
            else:
                return jsonify({"error": "Method not allowed"}), 405

        @self.flask_app.route('/todos/<int:id>', methods=['PUT'])
        async def mark_done_route(id):
            if self.mark_done(id) is not None:
                msg = json.dumps({"id": id, "operation": "updated"})
                await nats_send(msg)

                return redirect("/")
            else:
                return "Not Found", 404
        
        async def nats_send(msg: str):
            # Flask support asyncio is faily limited and every request
            # is executed in new event loop, thus a new connection must
            # be established every time
            nats_conn = await connect(NATS_URL)
            await nats_conn.publish("todo", msg.encode())
            await nats_conn.flush()
            await nats_conn.close()

    def run(self):
        self.flask_app.logger.info(f"Backend started in port {self.port}")
        self.flask_app.logger.info(f"Using Postgres at: {POSTGRES_URL}")
        self.flask_app.run(host='0.0.0.0', port=self.port)

backend_app = TodoBackend()
backend_app.init_db()
# asyncio.run(backend_app.init_nats())
flask_app = backend_app.flask_app

if __name__ == '__main__':
    flask_app.logger.setLevel(logging.INFO)
    backend_app.run()
else:
    import logging
    gunicorn_logger = logging.getLogger('gunicorn.error')
    flask_app.logger.handlers = gunicorn_logger.handlers
    flask_app.logger.setLevel(gunicorn_logger.level)
    flask_app.logger.info(f"Backend started in port {backend_app.port}")
