import enum, time, json, subprocess, os, uuid
from typing import Dict, Any
from redis import Redis
import psycopg2

class State(enum.Enum):
    PLAN_READY = "PLAN_READY"
    CONTEXT_READY = "CONTEXT_READY"
    CODING_ITERATION = "CODING_ITERATION"
    TESTING = "TESTING"
    REVIEW = "REVIEW"
    COMMIT_PENDING = "COMMIT_PENDING"
    DEPLOY = "DEPLOY"
    DONE = "DONE"
    FAILED = "FAILED"

class Orchestrator:
    def __init__(self, redis_url: str, audit_db: str):
        self.redis = Redis.from_url(redis_url)
        self.conn = psycopg2.connect(audit_db)

    def run_task(self, task: Dict[str, Any]):
        state = State.PLAN_READY
        ctx = {"iterations": 0, "max_iter": task["constraints"]["max_iterations"]}
        while state not in (State.DONE, State.FAILED):
            if state == State.PLAN_READY:
                plan = self._fetch_plan(task["id"])
                if not plan:
                    time.sleep(1); continue
                state = State.CONTEXT_READY
            elif state == State.CONTEXT_READY:
                self._build_context_index(task)
                state = State.CODING_ITERATION
            elif state == State.CODING_ITERATION:
                if ctx["iterations"] >= ctx["max_iter"]:
                    state = State.REVIEW
                else:
                    success = self._code_iteration(task, ctx)
                    state = State.TESTING if success else State.FAILED
            elif state == State.TESTING:
                test_ok = self._run_tests(task)
                state = State.REVIEW if test_ok else State.CODING_ITERATION
            elif state == State.REVIEW:
                if self._meets_acceptance(task):
                    state = State.COMMIT_PENDING
                else:
                    state = State.CODING_ITERATION
            elif state == State.COMMIT_PENDING:
                self._commit(task)
                state = State.DEPLOY if task.get("deploy") else State.DONE
            elif state == State.DEPLOY:
                self._deploy(task)
                state = State.DONE
        self._audit(task["id"], state.value)

    def _fetch_plan(self, task_id: str):
        key = f"plan:{task_id}"
        val = self.redis.get(key)
        return json.loads(val) if val else None

    def _build_context_index(self, task):
        # placeholder: trigger scanner
        self.redis.publish("events", json.dumps({"type":"context_build","task":task["id"]}))

    def _code_iteration(self, task, ctx):
        ctx["iterations"] += 1
        # spawn CodeLLM CLI inside a sandboxed container (placeholder command)
        task_dir = f"/work/{task['id']}"
        os.makedirs(task_dir, exist_ok=True)
        prompt = f"Goal: {task['goal']}\nAcceptance: {task['acceptance_criteria']}\nIteration: {ctx['iterations']}"
        with open(os.path.join(task_dir, "instruction.txt"), "w") as f:
            f.write(prompt)
        cmd = ["codellm", "run", "--input", "instruction.txt"]
        try:
            proc = subprocess.Popen(cmd, cwd=task_dir)
            proc.wait(timeout=300)
            return proc.returncode == 0
        except Exception as e:
            return False

    def _run_tests(self, task):
        # placeholder test runner
        return True

    def _meets_acceptance(self, task):
        return True  # placeholder

    def _commit(self, task):
        # git operations placeholder
        pass

    def _deploy(self, task):
        # trigger CD pipeline placeholder
        pass

    def _audit(self, task_id: str, final_state: str):
        cur = self.conn.cursor()
        cur.execute("insert into audits(task_id, state) values(%s,%s)", (task_id, final_state))
        self.conn.commit()