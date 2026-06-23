from flask import Blueprint, request, redirect, session, url_for
import uuid
from routes.quiz_questions import QUIZ_QUESTIONS
from datetime import datetime
from flask import make_response,render_template

quiz_bp = Blueprint("quiz", __name__)


DOMAINS = {
    "fingerprint": ["easy", "medium", "hard"],
    "questioned_documents": ["easy", "medium", "hard"],
    "forensic_biology_dna": ["easy", "medium", "hard"],
    "crime_scene_investigation": ["easy", "medium", "hard"],
    "cyber_forensics": ["easy", "medium", "hard"]
}


@quiz_bp.route('/quizzes')
def quizzes():
    return render_template(
        'quizzes.html',
        domains=DOMAINS
    )


@quiz_bp.route('/quiz/<domain>')
def levels(domain):

    return render_template(
        'levels.html',
        domain=domain
    )

def get_questions(domain, level):
    return QUIZ_QUESTIONS.get(domain, {}).get(level, [])

'''
@quiz_bp.route('/quiz/<domain>/<level>')
def start_quiz(domain, level):

    questions = get_questions(
        domain,
        level
    )

    return render_template(
        'quiz.html',
        domain=domain,
        level=level,
        questions=questions
    )'''

@quiz_bp.route('/quiz/<domain>/<level>')
def start_quiz(domain, level):

    questions = get_questions(domain, level)

    print(questions)

    return render_template(
        'quiz.html',
        domain=domain,
        level=level,
        questions=questions
    )


@quiz_bp.route('/submit_quiz', methods=['POST'])
def submit_quiz():

    name = request.form['name']
    email = request.form['email']

    domain = request.form['domain']
    level = request.form['level']

    questions = get_questions(
        domain,
        level
    )

    score = 0

    for q in questions:

        user_answer = request.form.get(
            f"q{q['id']}"
        )

        if user_answer == q["correct_answer"]:
            score += 1

    percentage = (
        score / len(questions)
    ) * 100

    session['student_name'] = name
    session['student_email'] = email
    session['domain'] = domain
    session['level'] = level
    session['score'] = score
    session['percentage'] = percentage

    if percentage >= 60:

        session['certificate_id'] = (
            "STS-" +
            str(uuid.uuid4())[:8].upper()
        )

        return redirect(
            url_for('quiz.certificate')
        )

    return render_template(
        'result.html',
        passed=False,
        score=score,
        percentage=percentage
    )


@quiz_bp.route('/certificate')
def certificate():

    if session.get('percentage', 0) < 60:
        return redirect('/quizzes')

    return render_template(
        "certificate.html",
        name=session.get('student_name'),
        domain=session.get('domain'),
        level=session.get('level'),
        score=session.get('score'),
        percentage=session.get('percentage'),
        certificate_id=session.get('certificate_id'),
        date=datetime.now().strftime("%d %B %Y")
    )

@quiz_bp.route('/download_certificate')
def download_certificate():

    if session.get('percentage', 0) < 60:
        return redirect('/quizzes')

    return render_template(
        "certificate_print.html",
        name=session.get('student_name'),
        domain=session.get('domain'),
        level=session.get('level'),
        score=session.get('score'),
        percentage=session.get('percentage'),
        certificate_id=session.get('certificate_id')
    )