from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/', methods=['GET'])
def run_bot():
    # bot.pyを実行する
    subprocess.Popen(['python', 'bot.py'])
    return 'Bot is running!'

if __name__ == '__main__':
    app.run(debug=True)
