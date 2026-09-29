import os
import sys
import signal
import subprocess
import tempfile
import hashlib
import re
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.chat_models import ChatOpenAI
from .state import AgentState

_FAILED = re.compile(r"^FAILED\s+(\S+)", re.M)
_ERR    = re.compile(r"^E\s+(.*)$", re.M)

def planner_node(state: AgentState) -> dict:
    llm = ChatOpenAI(temperature=0)
    task = state.get('task_description', '')
    prompt = f"Analyze this quantitative finance task and output a step-by-step logic plan. Focus on mathematical invariants. Task: {task}"
    
    response = llm.invoke([
        SystemMessage(content="You are an elite Quant Planner Agent."), 
        HumanMessage(content=prompt)
    ])
    return {"logic_plan": response.content, "stuck_loop": False}

def coder_node(state: AgentState) -> dict:
    llm = ChatOpenAI(temperature=0)
    logic_plan = state.get('logic_plan', '')
    last_traceback = state.get('last_traceback', '')
    
    prompt = f"Write Python code based on this logic plan:\n{logic_plan}\n\nEnsure it is robust."
    
    if last_traceback and not state.get('tests_passed'):
        prompt += f"\n\nPREVIOUS TEST FAILED. Condensed Traceback:\n{last_traceback}\n\nFIX THE CODE! Do not repeat the same error."
        
    response = llm.invoke([
        SystemMessage(content="You are an elite Quant Coder Agent. Output ONLY raw Python code. Do not wrap in markdown tags."), 
        HumanMessage(content=prompt)
    ])
    
    code = response.content
    if code.startswith("```python"): code = code[9:]
    if code.endswith("```"): code = code[:-3]
        
    return {"generated_code": code}

def _posix_limits(mem_mb: int, cpu_s: int):
    try:
        import resource
        def _preexec():
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_s, cpu_s))
            resource.setrlimit(resource.RLIMIT_AS, (mem_mb * 1024 * 1024,) * 2)
            resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
            resource.setrlimit(resource.RLIMIT_FSIZE, (64 * 1024 * 1024,) * 2)
        return _preexec
    except ImportError:
        return None

def executor_node(state: AgentState) -> dict:
    code = state.get('generated_code', '')
    timeout_s = 15
    
    with tempfile.TemporaryDirectory(prefix="quant_sandbox_") as tmpdir:
        test_file = os.path.join(tmpdir, "test_invariants.py")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(code)
            
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"}
        preexec = _posix_limits(1024, timeout_s) if os.name == "posix" else None

        try:
            proc = subprocess.Popen(
                [sys.executable, "-m", "pytest", "test_invariants.py", "-q", "-p", "no:cacheprovider", "--tb=short"],
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                start_new_session=True, # Own process group for safe reaping
                preexec_fn=preexec,
                env=env
            )
            out_b, err_b = proc.communicate(timeout=timeout_s)
            rc, timed_out = proc.returncode, False
        except subprocess.TimeoutExpired:
            if os.name == "posix":
                os.killpg(proc.pid, signal.SIGKILL)
            else:
                proc.kill()
            out_b, err_b = proc.communicate()
            rc, timed_out = -1, True
            
        stdout = out_b.decode("utf-8", errors="replace")[-8000:]
        stderr = err_b.decode("utf-8", errors="replace")[-8000:]
        if timed_out: 
            stderr += f"\n[EXECUTOR] TIMEOUT after {timeout_s}s"
            
    return {"test_results": stdout + "\n" + stderr, "tests_passed": rc == 0 and not timed_out}

def summarize_failure(stdout: str, stderr: str):
    failed = _FAILED.findall(stdout) or ["<unknown>"]
    errs = _ERR.findall(stdout) or [stderr.strip().splitlines()[-1] if stderr.strip() else "Unknown Error"]
    core = errs[-1][:500]
    sig = hashlib.sha256(f"{failed[0]}::{core}".encode()).hexdigest()[:16]
    return sig, f"Failing: {failed[:5]}\nError: {core}\n"

def reviewer_node(state: AgentState) -> dict:
    passed = state.get('tests_passed', False)
    if passed:
        return {"stuck_loop": False}
        
    sig, summary = summarize_failure(state.get('test_results', ''), "")
    stuck = (sig == state.get("last_error_signature", ""))
    
    return {
        "retry_count": state.get('retry_count', 0) + 1,
        "last_traceback": summary,
        "last_error_signature": sig,
        "stuck_loop": stuck
    }

def router(state: AgentState) -> str:
    if state.get('tests_passed'):
        return "END"
    if state.get('retry_count', 0) >= state.get('max_retries', 3):
        return "END" 
    if state.get('stuck_loop', False):
        return "planner_node" # Escalate to planner instead of blind retry
        
    return "coder_node"
