from supervise_web import core
from functools import wraps
from flask import Flask, render_template, abort, Response, request

app = Flask(__name__)


@app.before_request
def before_request():
    auth = request.authorization
    if not auth or not (core.config.get('Main', 'auth_username') == auth.username
                        and core.config.get('Main', 'auth_password') == auth.password):
        return Response('You need to be authenticated', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


@app.route('/')
def overview():
    return render_template('overview.html')


@app.route('/_daemons')
def _daemons():
    return render_template('_daemons.html', daemons=core.daemon_info())


@app.route('/daemon/<daemon_id>/_details')
def _details(daemon_id):
    return render_template('_details.html',
                           daemon_id=daemon_id,
                           run_file_content=core.run_file(daemon_id),
                           log_tail='to be implemented',
                           autostart=core.daemon_autostart(daemon_id))


@app.route('/daemon/<daemon_id>/<action>', methods=['POST'])
def daemon_action(daemon_id, action):
    if action == 'start':
        return Response(status=204) if core.start_daemon(daemon_id) else Response(status=500)
    elif action == 'stop':
        return Response(status=204) if core.stop_daemon(daemon_id) else Response(status=500)
    elif action == 'start_supervise':
        core.start_supervise(daemon_id)
        return Response(status=204)
    elif action == 'stop_supervise':
        core.stop_supervise(daemon_id)
        return Response(status=204)
    elif action == 'autostart':
        core.daemon_autostart(daemon_id, enabled=True)
        return Response(status=204)
    elif action == 'no_autostart':
        core.daemon_autostart(daemon_id, enabled=False)
        return Response(status=204)
    else:
        abort(400)