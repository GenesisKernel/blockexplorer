from flask import render_template, current_app as app
from flask import jsonify, request

from ....models.genesis.aux.config import (
    update_aux_db_engine_discovery_map
)
from ....models.genesis.aux.filler import Filler

#@app.route("/filler/test-add")
#def filler_test_add(x=16, y=16):
#    from ....celery.tasks import filler_test_add
#    x = int(request.args.get("x", x))
#    y = int(request.args.get("y", y))
#    res = filler_test_add.apply_async((x, y))
#    context = {"id": res.task_id, "x": x, "y": y}
#    result = "add((x){}, (y){})".format(context['x'], context['y'])
#    goto = "{}".format(context['id'])
#    return jsonify(result=result, goto=goto)
#
#@app.route("/filler/test-add/result/<task_id>")
#def filler_test_add_result(task_id):
#    from ....celery.tasks import filler_test_add
#    retval = filler_test_add.AsyncResult(task_id).get(timeout=20.0)
#    return repr(retval)
#
#@app.route("/filler/<int:seq_num>/update-common")
#def filler_update_common(seq_num):
#    #update_aux_db_engine_discovery_map(app)
#    update_aux_db_engine_discovery_map(app, force_update=True,
#                                       aux_db_engine_name_prefix='test_aux_')
#    f = Filler(app=app)
#    return jsonify(f.update())
#
#@app.route("/filler/<int:seq_num>/update")
#def filler_update(seq_num):
#    from ....celery.tasks import filler_update_task
#    res = filler_update_task.apply_async((seq_num,))
#    context = {"task_id": res.task_id, "seq_num": seq_num}
#    return jsonify(context)
#
#@app.route("/filler/<int:seq_num>/update/result/<task_id>")
#def filler_update_result(seq_num, task_id):
#    from ....celery.tasks import filler_update_task
#    retval = filler_update_task.AsyncResult(task_id).get(timeout=100.0)
#    return repr(retval)
#
#@app.route("/filler/<int:seq_num>/clear")
#def filler_clear(seq_num):
#    from ....celery.tasks import filler_clear_task
#    res = filler_clear_task.apply_async((seq_num,))
#    context = {"task_id": res.task_id, "seq_num": seq_num}
#    return jsonify(context)
#
#@app.route("/filler/<int:seq_num>/clear/result/<task_id>")
#def filler_clear_result(seq_num, task_id):
#    from ....celery.tasks import filler_clear_task
#    retval = filler_clear_task.AsyncResult(task_id).get(timeout=1.0)
#    return repr(retval)


