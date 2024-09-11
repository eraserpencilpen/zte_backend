from flask import Flask, request

app = Flask(__name__)
@app.route("/",methods=["POST"])
def base():
    return request.data
@app.route('/post_location', methods=['POST'])
def test_route():
    return f"Received: {request.data}"

if __name__ == '__main__':
    app.run(port=5000,debug=True,host="0.0.0.0")
