# System imports

# Third-party imports
from flask import Flask
from flask import jsonify

# Local source tree imports
import config

app = Flask(__name__)
con = config.CON


@app.route('/apps/', methods=['GET'])
def get_apps():
    app_dict = {"app": {}}
    app_names = con.smembers("apps")

    for app_name in app_names:
        app_dict["app"][app_name] = con.hgetall(app_name)
        app_dict["app"][app_name]["author"] = con.hgetall(con.hget(app_name,
                                                                   "author"))
        app_dict["app"][app_name]["ofversions"] = list(con.smembers
                                                       (con.hget
                                                        (app_name,
                                                         "ofversions")))
        app_dict["app"][app_name]["tags"] = list(con.smembers
                                                 (con.hget(app_name,
                                                           "tags")))
        app_dict["app"][app_name]["versions"] = list(con.smembers
                                                     (con.hget
                                                      (app_name,
                                                       "versions")))

    return jsonify(app_dict)


@app.route('/apps/<name>', methods=['GET'])
def get_app(name):
    app_dict = {"app": {}}

    app_dict["app"][name] = con.hgetall("app:"+name)
    app_dict["app"][name]["author"] = con.hgetall(con.hget
                                                  ("app:"+name, "author"))
    app_dict["app"][name]["ofversions"] = list(con.smembers
                                               (con.hget
                                                ("app:"+name, "ofversions")))
    app_dict["app"][name]["tags"] = list(con.smembers
                                         (con.hget("app:"+name, "tags")))
    app_dict["app"][name]["versions"] = list(con.smembers
                                             (con.hget
                                              ("app:"+name, "versions")))

    return jsonify(app_dict)


@app.route('/authors', methods=['GET'])
def get_authors():

    authors_dict = {"author": {}}
    authors_names = con.smembers("authors")

    for author_name in authors_names:
        authors_dict["author"][author_name] = con.hgetall(author_name)
        authors_dict["author"][author_name]["apps"] = list(con.smembers
                                                           (con.hget
                                                            (author_name,
                                                             "apps")))

        authors_dict["author"][author_name]["comments"] = list(con.smembers
                                                               (con.hget
                                                                (author_name,
                                                                 "comments")))

    return jsonify(authors_dict)


@app.route('/authors/<name>', methods=['GET'])
def get_author(name):

    author_dict = {"author": {}}

    author_dict["author"][name] = con.hgetall(name)
    author_dict["author"][name]["apps"] = list(con.smembers(con.hget
                                                            ("author:"+name,
                                                             "apps")))
    author_dict["author"][name]["comments"] = list(con.smembers
                                                   (con.hget
                                                    ("author:"+name,
                                                        "comments")))
    return jsonify(author_dict)


if __name__ == '__main__':
    app.run(debug=True)
