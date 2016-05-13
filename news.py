from flask import Flask, request, make_response
from bs4 import BeautifulSoup
import plivo, plivoxml, requests

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def inbound_sms():
    from_number = request.values.get('From')
    to_number = request.values.get('To')
    text = request.values.get('Text')
    print text

    body = ""
    try:
      body = text_response(text.split())
    except:
      body = "No text entered. Text a key word or phrase."

    if body == "":
      body =  "'" + text + "' not found. Try another word or phrase."
    params = {
      "src": to_number,
      "dst": from_number,
    }

    resp = plivoxml.Response()
    resp.addMessage(body, **params)

    ret_response = make_response(resp.to_xml())
    ret_response.headers["Content-type"] = "text/xml"

    return ret_response

def text_response(incoming_words):
    outgoing_text = ""
    max_num_common = 0
    respond = requests.get("https://en.wikipedia.org/wiki/Portal:Current_events")
    wiki = BeautifulSoup(respond.text, "html.parser")
    days = wiki.find_all('td', {'class':"description"})

    for day in days:
      events = day.find_all("ul",recursive=False)
      for event in events:
        descriptions = event.find_all("li",recursive=False)
        for description in descriptions:
          this_current_event = ""
          detailed_descriptions = description.find_all("li")
          if len(detailed_descriptions) > 0:
            for detailed_description in detailed_descriptions:
              this_current_event = this_current_event + detailed_description.text
          else:
            this_current_event = description.text

          num_in_common = 0
          split_this_current = this_current_event.split()
          for word in split_this_current:
            if word in incoming_words:
              num_in_common+=1

          if num_in_common>max_num_common:
            max_num_common = num_in_common
            outgoing_text = this_current_event
          elif num_in_common==max_num_common & num_in_common>0:
            outgoing_text = outgoing_text + " " + this_current_event

    return outgoing_text

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)