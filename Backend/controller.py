from app import app
from model import demo
@app.route('/demotest',methods=['GET'])
def fetch_code_from_repo():
  demo_obj = demo()
  return demo_obj.fetch_code_from_repo()

from flask import jsonify,request
from model.kubernetesmodel import KubernetesModel
from app import app

@app.route('/clusters', methods=['GET'])
def get_clusters():
    try:
        model = KubernetesModel()  # Instantiate the class here
        clusters = model.list_aks_clusters()  # Now call the method on the instance
        return jsonify(clusters), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/clusters/nodes/usage', methods=['GET'])
def get_node_usage():
    try:
        cluster_name=request.args.get('clustername')
        model = KubernetesModel()
        usage = model.get_node_usage(cluster_name)
        return jsonify(usage), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@app.route('/clusters/cpu/summary', methods=['GET'])
def get_cpu_summary():
    try:
        cluster_name=request.args.get('clustername')
        model = KubernetesModel()
        summary = model.get_cpu_summary(cluster_name)
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/clusters/memory/summary', methods=['GET'])
def get_memory_summary():
    try:
        cluster_name=request.args.get('clustername')
        model = KubernetesModel()
        summary = model.get_memory_summary(cluster_name)
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
