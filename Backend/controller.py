from app import app
from model import demo
#code controller here it is
@app.route('/demotest',methods=['GET'])
def fetch_code_from_repo():
  demo_obj = demo()
  return demo_obj.fetch_code_from_repo()
