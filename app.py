from flask import Flask, render_template, request, url_for, redirect, session
import GoogleNLPAPI as api
import getYoutubeVideoLinks as getYT
import emailer as email
import speech_recognition as sr
from emailAnalysis import send_email

# import summarizer as summ


app = Flask(__name__)
app.secret_key = 'thisisasecretkey'


@app.route('/delallsessions')
def delallsessions():
    session.pop('transcript', None)
    session.pop('summary', None)
    session.pop('keywords', None)
    session.pop('email_sent', None)
    return redirect('/')


@app.route('/', methods=['GET', 'POST'])
def index():
    # session.pop('transcript', None)
    # session.pop('summary', None)
    # session.pop('keywords', None)
    return render_template('index.html', session=session)


@app.route('/record')
def record():
    return render_template('record.html')


@app.route('/delsession', methods=['GET', 'POST'])
def delscript():
    session.pop('transcript', None)
    session.pop('summary', None)
    session.pop('keywords', None)
    return redirect('/convertwav')


@app.route('/textanalysis', methods=['GET', 'POST'])
def textanalysis():
    if 'transcript' in session:
        if request.method == 'POST':
            emailform = request.form
            reciever = emailform['email']
            subject = emailform['subject']
            send_email(f"{subject} - Your AudioLec Lecture", session['transcript'], reciever,
                       'hackathon2020', 'audiolec4@gmail.com')
        keywords = api.sample_analyze_entities(session['transcript'])
        session['keywords'] = keywords
        return render_template('textanalysis.html', session=session)
    else:
        return redirect('/convertwav')


@app.route('/testintelligence', methods=['GET', 'POST'])
def testintelligence():
    if 'transcript' in session:
        if request.method == 'POST':
            emailform = request.form
            reciever = emailform['email']
            subject = emailform['subject']
            send_email(f"{subject} - Your AudioLec Lecture", session['transcript'], reciever,
                       'hackathon2020', 'audiolec4@gmail.com')
        keywords = api.sample_analyze_entities(session['transcript'])
        session['keywords'] = keywords

        videos = []
        people = []
        places = []
        if 'keywords' in session:
            for catergory, keywords in session['keywords'].items():
                for keyword in keywords:
                    video = getYT.searchVideoForKeyword(keyword)
                    for indivvideo in video:
                        if catergory == "people":
                            people.append(f'{indivvideo}')
                        elif catergory == "placesOrOrganizations":
                            places.append(f'{indivvideo}')
                        videos.append(f'{indivvideo}')
            print(people)
            print(places)


        return render_template('testintelligence.html', session=session,videos=videos, places=places, people=people, lenplaces=len(places),
                           lenpeople=len(people))

    else:
        return redirect('/convertwav')


@app.route('/youtubevids')
def youtubevids():
    videos = []
    people = []
    places = []
    if 'keywords' in session:
        for catergory, keywords in session['keywords'].items():
            for keyword in keywords:
                video = getYT.searchVideoForKeyword(keyword)
                for indivvideo in video:
                    if catergory == "people":
                        people.append(f'{indivvideo}')
                    elif catergory == "placesOrOrganizations":
                        places.append(f'{indivvideo}')
                    videos.append(f'{indivvideo}')
        print(people)
        print(places)
        return render_template('videos.html', videos=videos, places=places, people=people, lenplaces=len(places), lenpeople=len(people))
    else:
        return redirect('/convertwav')


@app.route('/convertwav', methods=['GET', 'POST'])
def convertwav():
    transcript = ""
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)

        if file:
            recognizer = sr.Recognizer()
            audioFile = sr.AudioFile(file)
            with audioFile as source:
                recognizer.adjust_for_ambient_noise(source)
                data = recognizer.record(source)
            transcript = recognizer.recognize_google(data, key=None)
            session['transcript'] = transcript
            print("transcript: " + transcript)
            return redirect('/textanalysis')  # change in later/test


    return render_template('convertwav.html')


@app.route('/contactform', methods=['GET', 'POST'])
def contactform():
    session['valid'] = True
    contactform = request.form
    sender_email = contactform['email']
    subject = contactform['subject'] + f" by: {sender_email}"
    msg = contactform['message']
    if email == "" or subject == "" or msg == "":
        session['valid'] = False
    else:
        email.send_email(subject, msg, 'audiolec4@gmail.com',
                         'hackathon2020', 'audiolec4@gmail.com')
        session['email_sent'] = True
        return redirect('/#footer')
    return redirect('/#footer')


@app.route('/generic')
def generic():
    return render_template('generic.html')


if __name__ == '__main__':
    app.run(debug=True)
