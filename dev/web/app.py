import black
import textwrap

from flask import Flask, render_template, request
from swinginghead.compiler import Binder
from io import StringIO
from contextlib import redirect_stdout

app = Flask(__name__)

DEFAULT_SOURCE = """
swing `float` $`float`€`float`$
head {
    |,1 >f ordered gt< ,2| => {
        ./ (`float`->2.0)
    }
    !=> {
        ./ (`float`->5.0)
    }
    ./ ,2
}
"""
DEFAULT_PYSOURCE = """
print(swh.head(3.5, 3.4))
"""
DEFAULT_RESULT = ""
@app.route("/", methods=["POST", "GET"])
def index():
    source = request.form.get("source") or DEFAULT_SOURCE
    pysource = request.form.get("pysource") or DEFAULT_PYSOURCE
    try:
        binder = Binder(source)
        result = StringIO()
        with redirect_stdout(result):
            exec(pysource, {"swh": binder})
        result = result.getvalue()
        exception = None
    except Exception as exc:
        result = ""
        exception = exc
        
    
    data = {
        "source": source,
        "pysource": pysource,
        "result": result,
        "error": exception
    }

    return render_template("index.html", **data)


if __name__ == "__main__":
    app.run(debug=True)
