from flask import Flask, render_template


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', title='Home')


@app.route('/search')
def search():
    return render_template('search.html', title='Search Result')


if __name__ == '__main__':
    app.run(debug=True)
