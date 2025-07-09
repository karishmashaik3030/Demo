from app import app
from model import demo
@app.route('/demotest',methods=['GET'])
def fetch_code_from_repo():
  demo_obj = demo()
  return demo_obj.fetch_code_from_repo()
