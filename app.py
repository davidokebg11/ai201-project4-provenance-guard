import uuid
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

from detector import detect_with_llm
from stylometrics import compute_stylometrics
from scorer import combine_scores
from labeler import generate_label
from auditor import log_submission, log_appeal, get_log

load_dotenv()

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)


@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute;100 per day")
def submit():
    data = request.get_json()

    if not data or "text" not in data or "creator_id" not in data:
        return jsonify({"error": "Request must include 'text' and 'creator_id'"}), 400

    text = data["text"]
    creator_id = data["creator_id"]

    if len(text.strip()) < 20:
        return jsonify({"error": "Text is too short for analysis (minimum 20 characters)"}), 400

    # Run both detection signals
    llm_score = detect_with_llm(text)
    stylo_score = compute_stylometrics(text)

    # Combine into confidence score + attribution
    result = combine_scores(llm_score, stylo_score)

    # Generate transparency label
    label = generate_label(result["attribution"], result["confidence"])

    # Generate unique content ID
    content_id = str(uuid.uuid4())

    # Write to audit log
    log_submission(
        content_id=content_id,
        creator_id=creator_id,
        attribution=result["attribution"],
        confidence=result["confidence"],
        llm_score=result["llm_score"],
        stylo_score=result["stylo_score"],
    )

    return jsonify({
        "content_id": content_id,
        "attribution": result["attribution"],
        "confidence": result["confidence"],
        "llm_score": result["llm_score"],
        "stylo_score": result["stylo_score"],
        "label": label,
    })


@app.route("/appeal", methods=["POST"])
def appeal():
    data = request.get_json()

    if not data or "content_id" not in data or "creator_reasoning" not in data:
        return jsonify({"error": "Request must include 'content_id' and 'creator_reasoning'"}), 400

    content_id = data["content_id"]
    creator_reasoning = data["creator_reasoning"]

    updated = log_appeal(content_id, creator_reasoning)

    if not updated:
        return jsonify({"error": "content_id not found in audit log"}), 404

    return jsonify({
        "message": "Appeal received successfully.",
        "content_id": content_id,
        "status": "under_review",
    })


@app.route("/log", methods=["GET"])
def log():
    entries = get_log()
    return jsonify({"entries": entries, "total": len(entries)})


if __name__ == "__main__":
    app.run(debug=True)