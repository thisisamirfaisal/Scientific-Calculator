"""
Advanced Scientific Calculator — Streamlit App
Deployable on Hugging Face Spaces & Google Colab
"""

import streamlit as st
import math
import re
from collections import deque
from typing import Optional

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Scientific Calculator",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
PHI = (1 + math.sqrt(5)) / 2          # Golden ratio
MAX_HISTORY = 10                        # Maximum entries kept in history
MAX_EXPR_LEN = 64                       # Guard against absurdly long input

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
def inject_css() -> None:
    st.markdown(
        """
        <style>
        /* ── Google Fonts ── */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;700;800&display=swap');

        /* ── Global reset & background ── */
        html, body, [data-testid="stAppViewContainer"] {
            background: #0d0f14 !important;
            color: #e2e8f0;
            font-family: 'Syne', sans-serif;
        }
        [data-testid="stHeader"] { background: transparent !important; }
        [data-testid="stToolbar"] { display: none; }
        footer { display: none !important; }
        [data-testid="stSidebar"] { display: none; }

        /* ── Main container ── */
        .block-container {
            max-width: 520px !important;
            padding: 1.5rem 1rem 2rem !important;
            margin: 0 auto;
        }

        /* ── Title ── */
        .calc-title {
            font-family: 'Syne', sans-serif;
            font-weight: 800;
            font-size: 1.4rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #7ee8fa;
            text-align: center;
            margin-bottom: 0.2rem;
        }
        .calc-subtitle {
            text-align: center;
            font-size: 0.7rem;
            letter-spacing: 0.2em;
            color: #4a5568;
            margin-bottom: 1.2rem;
            text-transform: uppercase;
        }

        /* ── Display screen ── */
        .display-box {
            background: #080a0f;
            border: 1px solid #1e2533;
            border-radius: 12px;
            padding: 1rem 1.2rem 0.8rem;
            margin-bottom: 1rem;
            min-height: 90px;
            box-shadow: inset 0 2px 12px rgba(0,0,0,0.6), 0 0 0 1px #0f1520;
        }
        .display-expr {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: #4a6fa5;
            min-height: 1.2em;
            word-break: break-all;
            margin-bottom: 0.3rem;
        }
        .display-result {
            font-family: 'JetBrains Mono', monospace;
            font-size: 2rem;
            font-weight: 700;
            color: #7ee8fa;
            text-align: right;
            word-break: break-all;
            text-shadow: 0 0 20px rgba(126,232,250,0.25);
        }
        .display-result.error {
            color: #fc8181;
            font-size: 1rem;
            text-shadow: none;
        }

        /* ── Mode / memory badges ── */
        .badge-row {
            display: flex;
            gap: 0.4rem;
            margin-bottom: 0.8rem;
            flex-wrap: wrap;
        }
        .badge {
            font-size: 0.6rem;
            letter-spacing: 0.15em;
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: 700;
            text-transform: uppercase;
        }
        .badge-mode   { background: #1a2744; color: #7ee8fa; border: 1px solid #2d4a7a; }
        .badge-mem    { background: #1a2d1a; color: #68d391; border: 1px solid #276749; }
        .badge-mem-empty { background: #1a1a1a; color: #4a5568; border: 1px solid #2d2d2d; }

        /* ── Section label ── */
        .section-label {
            font-size: 0.6rem;
            letter-spacing: 0.2em;
            color: #4a5568;
            text-transform: uppercase;
            margin: 0.5rem 0 0.3rem;
        }

        /* ── Calc buttons ── */
        div[data-testid="column"] > div > div > div > div[data-testid="stButton"] > button {
            width: 100%;
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            font-weight: 600;
            padding: 0.55rem 0.2rem;
            border: 1px solid transparent;
            transition: all 0.12s ease;
            cursor: pointer;
            letter-spacing: 0.02em;
        }

        /* Digit buttons */
        .btn-digit > div > div > div > div[data-testid="stButton"] > button {
            background: #161b26;
            color: #e2e8f0;
            border-color: #1e2533;
        }
        .btn-digit > div > div > div > div[data-testid="stButton"] > button:hover {
            background: #1e2840;
            border-color: #3a5080;
            color: #fff;
        }

        /* Operator buttons */
        .btn-op > div > div > div > div[data-testid="stButton"] > button {
            background: #0f2040;
            color: #7ee8fa;
            border-color: #1e3a60;
        }
        .btn-op > div > div > div > div[data-testid="stButton"] > button:hover {
            background: #1a3060;
            border-color: #4a90d9;
        }

        /* Function buttons */
        .btn-fn > div > div > div > div[data-testid="stButton"] > button {
            background: #111820;
            color: #a0aec0;
            border-color: #1e2533;
            font-size: 0.72rem;
        }
        .btn-fn > div > div > div > div[data-testid="stButton"] > button:hover {
            background: #1a2430;
            color: #e2e8f0;
        }

        /* Equals button */
        .btn-eq > div > div > div > div[data-testid="stButton"] > button {
            background: linear-gradient(135deg, #1a6ba0, #0e4d7a);
            color: #7ee8fa;
            border-color: #2a8ac8;
            font-size: 1.1rem;
        }
        .btn-eq > div > div > div > div[data-testid="stButton"] > button:hover {
            background: linear-gradient(135deg, #2280c0, #1060a0);
            box-shadow: 0 0 14px rgba(126,232,250,0.2);
        }

        /* Clear / backspace */
        .btn-clear > div > div > div > div[data-testid="stButton"] > button {
            background: #2d1515;
            color: #fc8181;
            border-color: #5a2020;
        }
        .btn-clear > div > div > div > div[data-testid="stButton"] > button:hover {
            background: #3d1a1a;
        }

        /* Memory buttons */
        .btn-mem > div > div > div > div[data-testid="stButton"] > button {
            background: #0f2018;
            color: #68d391;
            border-color: #1a4030;
            font-size: 0.72rem;
        }
        .btn-mem > div > div > div > div[data-testid="stButton"] > button:hover {
            background: #182d22;
        }

        /* Constant buttons */
        .btn-const > div > div > div > div[data-testid="stButton"] > button {
            background: #1a1528;
            color: #b794f4;
            border-color: #2d2050;
            font-size: 0.75rem;
        }
        .btn-const > div > div > div > div[data-testid="stButton"] > button:hover {
            background: #221c38;
        }

        /* ── History panel ── */
        .history-box {
            background: #080a0f;
            border: 1px solid #1e2533;
            border-radius: 10px;
            padding: 0.8rem 1rem;
            margin-top: 0.8rem;
            max-height: 200px;
            overflow-y: auto;
        }
        .history-title {
            font-size: 0.6rem;
            letter-spacing: 0.2em;
            color: #4a5568;
            text-transform: uppercase;
            margin-bottom: 0.6rem;
        }
        .history-entry {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: #4a6a90;
            border-bottom: 1px solid #0f1520;
            padding: 0.3rem 0;
            display: flex;
            justify-content: space-between;
            gap: 1rem;
        }
        .history-entry:last-child { border-bottom: none; }
        .history-result { color: #7ee8fa; font-weight: 600; }
        .history-empty {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: #2d3748;
            text-align: center;
            padding: 0.5rem;
        }

        /* ── Divider ── */
        hr {
            border: none;
            border-top: 1px solid #1e2533;
            margin: 0.6rem 0;
        }

        /* ── Scrollbar ── */
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: #0d0f14; }
        ::-webkit-scrollbar-thumb { background: #1e2533; border-radius: 2px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
def init_state() -> None:
    """Initialise all session-state keys on first run."""
    defaults = {
        "expression": "",          # Current expression string shown in display
        "result": "0",             # Computed result (string for display)
        "error": "",               # Error message if last eval failed
        "memory": None,            # Stored memory value (float | None)
        "history": deque(maxlen=MAX_HISTORY),  # (expr, result) pairs
        "angle_mode": "DEG",       # "DEG" or "RAD"
        "just_evaluated": False,   # True right after pressing =
        "shift": False,            # Shift (2nd) mode for inverse trig etc.
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ─────────────────────────────────────────────
#  EXPRESSION BUILDING
# ─────────────────────────────────────────────
def append_to_expr(token: str) -> None:
    """
    Append a token to the current expression.
    If the last action was an evaluation, start fresh for digit/const tokens
    but allow operator continuation.
    """
    expr = st.session_state.expression
    just_eval = st.session_state.just_evaluated

    if just_eval:
        # After evaluation: operators continue from result; everything else resets
        if token in ("+", "-", "×", "÷", "^", "%", ")"):
            # Carry result into new expression
            expr = st.session_state.result
        else:
            expr = ""
        st.session_state.just_evaluated = False

    # Guard against runaway input
    if len(expr) >= MAX_EXPR_LEN:
        return

    st.session_state.expression = expr + token


def backspace() -> None:
    """Remove the last character from the expression."""
    st.session_state.just_evaluated = False
    st.session_state.expression = st.session_state.expression[:-1]
    st.session_state.error = ""


def clear_all() -> None:
    """Reset expression, result, and error but keep memory and history."""
    st.session_state.expression = ""
    st.session_state.result = "0"
    st.session_state.error = ""
    st.session_state.just_evaluated = False


# ─────────────────────────────────────────────
#  SAFE EXPRESSION EVALUATOR
# ─────────────────────────────────────────────
def _to_rad(x: float) -> float:
    """Convert to radians if the calculator is in DEG mode."""
    return math.radians(x) if st.session_state.angle_mode == "DEG" else x


def _from_rad(x: float) -> float:
    """Convert from radians if the calculator is in DEG mode."""
    return math.degrees(x) if st.session_state.angle_mode == "DEG" else x


def _build_safe_namespace() -> dict:
    """
    Build the evaluation namespace exposing only safe math symbols.
    Operators like × and ÷ are replaced before eval, so this namespace
    covers function names used in expressions like sin(30).
    """
    return {
        # Trig (input in current angle mode)
        "sin":   lambda x: math.sin(_to_rad(x)),
        "cos":   lambda x: math.cos(_to_rad(x)),
        "tan":   lambda x: math.tan(_to_rad(x)),
        # Inverse trig (output in current angle mode)
        "asin":  lambda x: _from_rad(math.asin(x)),
        "acos":  lambda x: _from_rad(math.acos(x)),
        "atan":  lambda x: _from_rad(math.atan(x)),
        "atan2": lambda y, x: _from_rad(math.atan2(y, x)),
        # Hyperbolic
        "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
        "asinh": math.asinh, "acosh": math.acosh, "atanh": math.atanh,
        # Logarithms
        "log":  math.log10,      # log() = log base-10
        "ln":   math.log,        # ln()  = natural log
        "log2": math.log2,
        # Roots & powers
        "sqrt": math.sqrt,
        "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x),
        "nrt":  lambda n, x: math.copysign(abs(x) ** (1 / n), x),
        "exp":  math.exp,
        # Misc
        "factorial": math.factorial,
        "abs":   abs,
        "floor": math.floor,
        "ceil":  math.ceil,
        "round": round,
        "gcd":   math.gcd,
        # Constants
        "pi":  math.pi,
        "e":   math.e,
        "phi": PHI,
        "inf": math.inf,
        "tau": math.tau,
        # Builtins we allow
        "__builtins__": {},
    }


def _preprocess(expr: str) -> str:
    """
    Transform display-friendly operators into Python-evaluable syntax.
    e.g.  3×4 → 3*4,  8÷2 → 8/2,  2^10 → 2**10,  5! → factorial(5)
    """
    expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**")
    expr = expr.replace("π", "pi").replace("φ", "phi")
    # Convert 5! → factorial(5) — handles integers only
    expr = re.sub(r"(\d+)!", r"factorial(\1)", expr)
    # Fix implicit multiplication: 2π → 2*pi, 3e → 3*e, 2( → 2*(
    expr = re.sub(r"(\d)(pi|phi|e\b|\()", r"\1*\2", expr)
    return expr


def evaluate_expression(expr: str) -> tuple[Optional[float], str]:
    """
    Safely evaluate the expression string.
    Returns (value, error_message). If successful, error_message is "".
    """
    if not expr.strip():
        return None, "Empty expression"

    processed = _preprocess(expr)

    try:
        result = eval(processed, {"__builtins__": {}}, _build_safe_namespace())  # noqa: S307
    except ZeroDivisionError:
        return None, "Division by zero"
    except ValueError as exc:
        return None, f"Math error: {exc}"
    except OverflowError:
        return None, "Result too large (overflow)"
    except (SyntaxError, NameError, TypeError) as exc:
        return None, f"Invalid expression: {exc}"
    except Exception as exc:  # catch-all safety net
        return None, f"Error: {exc}"

    if not isinstance(result, (int, float)):
        return None, "Non-numeric result"
    if math.isnan(result):
        return None, "Result is NaN"
    if math.isinf(result):
        return None, "Result is Infinity"

    return float(result), ""


def do_evaluate() -> None:
    """
    Called when the user presses =.
    Evaluate the current expression, update result/history/state.
    """
    expr = st.session_state.expression
    if not expr:
        return

    value, error = evaluate_expression(expr)

    if error:
        st.session_state.error = error
        st.session_state.result = "Error"
    else:
        # Format: show integer if it's whole, else up to 10 sig-figs
        if value == int(value) and abs(value) < 1e15:
            formatted = str(int(value))
        else:
            formatted = f"{value:.10g}"

        st.session_state.result = formatted
        st.session_state.error = ""
        # Push to history
        st.session_state.history.appendleft((expr, formatted))

    st.session_state.just_evaluated = True


# ─────────────────────────────────────────────
#  MEMORY FUNCTIONS
# ─────────────────────────────────────────────
def memory_store_add() -> None:
    """M+ : add current result to memory."""
    val, err = evaluate_expression(st.session_state.expression or st.session_state.result)
    if not err:
        st.session_state.memory = (st.session_state.memory or 0) + val


def memory_store_sub() -> None:
    """M− : subtract current result from memory."""
    val, err = evaluate_expression(st.session_state.expression or st.session_state.result)
    if not err:
        st.session_state.memory = (st.session_state.memory or 0) - val


def memory_recall() -> None:
    """MR : recall memory value into expression."""
    if st.session_state.memory is not None:
        append_to_expr(f"{st.session_state.memory:.10g}")


def memory_clear() -> None:
    """MC : clear memory."""
    st.session_state.memory = None


# ─────────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────────
def btn(label: str, action, cols, idx: int, style_class: str = "btn-digit"):
    """Render a single calculator button inside a pre-built column."""
    with cols[idx]:
        st.markdown(f'<div class="{style_class}">', unsafe_allow_html=True)
        if st.button(label, key=f"btn_{label}_{idx}_{style_class}"):
            action()
        st.markdown("</div>", unsafe_allow_html=True)


def make_cols(n: int):
    """Return n equal-width streamlit columns."""
    return st.columns([1] * n)


# ─────────────────────────────────────────────
#  DISPLAY
# ─────────────────────────────────────────────
def render_display() -> None:
    expr = st.session_state.expression or ""
    result = st.session_state.result
    error = st.session_state.error

    result_class = "display-result error" if error else "display-result"
    display_val = error if error else result

    st.markdown(
        f"""
        <div class="display-box">
            <div class="display-expr">{expr or "&nbsp;"}</div>
            <div class="{result_class}">{display_val}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_badges() -> None:
    mode = st.session_state.angle_mode
    mem = st.session_state.memory
    mem_badge = (
        f'<span class="badge badge-mem">M = {mem:.6g}</span>'
        if mem is not None
        else '<span class="badge badge-mem-empty">M: –</span>'
    )
    st.markdown(
        f"""
        <div class="badge-row">
            <span class="badge badge-mode">{mode}</span>
            {mem_badge}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_history() -> None:
    history = st.session_state.history
    st.markdown('<div class="history-box">', unsafe_allow_html=True)
    st.markdown('<div class="history-title">▸ History</div>', unsafe_allow_html=True)
    if not history:
        st.markdown('<div class="history-empty">No calculations yet</div>', unsafe_allow_html=True)
    else:
        for expr, res in history:
            safe_expr = expr.replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(
                f'<div class="history-entry">'
                f'<span>{safe_expr}</span>'
                f'<span class="history-result">= {res}</span>'
                f"</div>",
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  BUTTON GRID RENDERING
# ─────────────────────────────────────────────
def render_memory_row() -> None:
    st.markdown('<p class="section-label">Memory</p>', unsafe_allow_html=True)
    cols = make_cols(4)
    with cols[0]:
        st.markdown('<div class="btn-mem">', unsafe_allow_html=True)
        if st.button("M+", key="mem_add"):
            memory_store_add()
        st.markdown("</div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown('<div class="btn-mem">', unsafe_allow_html=True)
        if st.button("M−", key="mem_sub"):
            memory_store_sub()
        st.markdown("</div>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown('<div class="btn-mem">', unsafe_allow_html=True)
        if st.button("MR", key="mem_recall"):
            memory_recall()
        st.markdown("</div>", unsafe_allow_html=True)
    with cols[3]:
        st.markdown('<div class="btn-mem">', unsafe_allow_html=True)
        if st.button("MC", key="mem_clear"):
            memory_clear()
        st.markdown("</div>", unsafe_allow_html=True)


def render_mode_row() -> None:
    st.markdown('<p class="section-label">Mode & Utility</p>', unsafe_allow_html=True)
    cols = make_cols(4)

    # Angle mode toggle
    with cols[0]:
        st.markdown('<div class="btn-fn">', unsafe_allow_html=True)
        if st.button(
            "DEG" if st.session_state.angle_mode == "RAD" else "RAD",
            key="toggle_angle",
        ):
            st.session_state.angle_mode = (
                "RAD" if st.session_state.angle_mode == "DEG" else "DEG"
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with cols[1]:
        st.markdown('<div class="btn-fn">', unsafe_allow_html=True)
        if st.button("( )", key="btn_paren"):
            # Smart parenthesis: opens if unclosed, else closes
            expr = st.session_state.expression
            open_count = expr.count("(") - expr.count(")")
            append_to_expr("(" if open_count == 0 else ")")
        st.markdown("</div>", unsafe_allow_html=True)

    with cols[2]:
        st.markdown('<div class="btn-clear">', unsafe_allow_html=True)
        if st.button("⌫", key="btn_back"):
            backspace()
        st.markdown("</div>", unsafe_allow_html=True)

    with cols[3]:
        st.markdown('<div class="btn-clear">', unsafe_allow_html=True)
        if st.button("AC", key="btn_ac"):
            clear_all()
        st.markdown("</div>", unsafe_allow_html=True)


def render_scientific_row1() -> None:
    """sin, cos, tan, ln, log"""
    cols = make_cols(5)
    fns = [
        ("sin", "sin("),
        ("cos", "cos("),
        ("tan", "tan("),
        ("ln",  "ln("),
        ("log", "log("),
    ]
    for i, (label, token) in enumerate(fns):
        with cols[i]:
            st.markdown('<div class="btn-fn">', unsafe_allow_html=True)
            if st.button(label, key=f"fn_{label}"):
                append_to_expr(token)
            st.markdown("</div>", unsafe_allow_html=True)


def render_scientific_row2() -> None:
    """asin, acos, atan, √, ∛"""
    cols = make_cols(5)
    fns = [
        ("asin", "asin("),
        ("acos", "acos("),
        ("atan", "atan("),
        ("√",    "sqrt("),
        ("∛",    "cbrt("),
    ]
    for i, (label, token) in enumerate(fns):
        with cols[i]:
            st.markdown('<div class="btn-fn">', unsafe_allow_html=True)
            if st.button(label, key=f"fn2_{label}"):
                append_to_expr(token)
            st.markdown("</div>", unsafe_allow_html=True)


def render_scientific_row3() -> None:
    """sinh, cosh, tanh, x!, |x|"""
    cols = make_cols(5)
    fns = [
        ("sinh", "sinh("),
        ("cosh", "cosh("),
        ("tanh", "tanh("),
        ("x!",   "!"),
        ("|x|",  "abs("),
    ]
    for i, (label, token) in enumerate(fns):
        with cols[i]:
            st.markdown('<div class="btn-fn">', unsafe_allow_html=True)
            if st.button(label, key=f"fn3_{label}"):
                append_to_expr(token)
            st.markdown("</div>", unsafe_allow_html=True)


def render_scientific_row4() -> None:
    """floor, ceil, exp, nrt(, log2"""
    cols = make_cols(5)
    fns = [
        ("⌊x⌋", "floor("),
        ("⌈x⌉", "ceil("),
        ("eˣ",  "exp("),
        ("ⁿ√x", "nrt("),
        ("log₂", "log2("),
    ]
    for i, (label, token) in enumerate(fns):
        with cols[i]:
            st.markdown('<div class="btn-fn">', unsafe_allow_html=True)
            if st.button(label, key=f"fn4_{label}"):
                append_to_expr(token)
            st.markdown("</div>", unsafe_allow_html=True)


def render_constants_row() -> None:
    cols = make_cols(5)
    consts = [
        ("π",  "π"),
        ("e",  "e"),
        ("φ",  "φ"),
        ("τ",  "tau"),
        ("∞",  "inf"),
    ]
    for i, (label, token) in enumerate(consts):
        with cols[i]:
            st.markdown('<div class="btn-const">', unsafe_allow_html=True)
            if st.button(label, key=f"const_{label}"):
                append_to_expr(token)
            st.markdown("</div>", unsafe_allow_html=True)


def render_main_pad() -> None:
    """Main digit + operator pad (4×4 + equals row)."""
    st.markdown('<p class="section-label">Digits & Operators</p>', unsafe_allow_html=True)

    rows = [
        [("7","btn-digit"), ("8","btn-digit"), ("9","btn-digit"), ("÷","btn-op")],
        [("4","btn-digit"), ("5","btn-digit"), ("6","btn-digit"), ("×","btn-op")],
        [("1","btn-digit"), ("2","btn-digit"), ("3","btn-digit"), ("−","btn-op")],
        [("0","btn-digit"), (".","btn-digit"), ("%","btn-op"),   ("+","btn-op")],
    ]
    op_map = {"÷": "÷", "×": "×", "−": "-", "+": "+", "%": "%"}

    for row in rows:
        cols = make_cols(4)
        for i, (label, style) in enumerate(row):
            token = op_map.get(label, label)
            with cols[i]:
                st.markdown(f'<div class="{style}">', unsafe_allow_html=True)
                if st.button(label, key=f"pad_{label}_{style}"):
                    append_to_expr(token)
                st.markdown("</div>", unsafe_allow_html=True)

    # Bottom row: ^ (power), +/- sign, = 
    cols = make_cols(3)
    with cols[0]:
        st.markdown('<div class="btn-op">', unsafe_allow_html=True)
        if st.button("xʸ", key="btn_pow"):
            append_to_expr("^")
        st.markdown("</div>", unsafe_allow_html=True)

    with cols[1]:
        st.markdown('<div class="btn-digit">', unsafe_allow_html=True)
        if st.button("+/−", key="btn_sign"):
            # Negate: wrap current expression or prepend minus
            expr = st.session_state.expression
            if expr.startswith("-"):
                st.session_state.expression = expr[1:]
            else:
                st.session_state.expression = "-" + expr
        st.markdown("</div>", unsafe_allow_html=True)

    with cols[2]:
        st.markdown('<div class="btn-eq">', unsafe_allow_html=True)
        if st.button("=", key="btn_eq"):
            do_evaluate()
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────
def main() -> None:
    inject_css()
    init_state()

    # Title
    st.markdown('<div class="calc-title">🧮 Scientific Calc</div>', unsafe_allow_html=True)
    st.markdown('<div class="calc-subtitle">Advanced • Stateful • Dark Edition</div>', unsafe_allow_html=True)

    # Display
    render_display()
    render_badges()

    st.markdown("<hr>", unsafe_allow_html=True)

    # Scientific function rows
    render_scientific_row1()
    render_scientific_row2()
    render_scientific_row3()
    render_scientific_row4()

    st.markdown("<hr>", unsafe_allow_html=True)

    # Constants
    render_constants_row()

    st.markdown("<hr>", unsafe_allow_html=True)

    # Memory + mode controls
    render_memory_row()
    render_mode_row()

    st.markdown("<hr>", unsafe_allow_html=True)

    # Main digit pad
    render_main_pad()

    # History
    render_history()


# Streamlit re-executes this file top-to-bottom on every interaction.
# Calling main() at module scope (not inside __name__ == "__main__") is the
# correct pattern — it ensures the ScriptRunContext is always established
# before any st.* call, eliminating the "missing ScriptRunContext" warnings
# that appear when the guard causes execution to be deferred.
main()