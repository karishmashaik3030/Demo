from app import app
from model import demo
#code controller code here is code the code
@app.route('/demotest',methods=['GET'])
def fetch_code_from_repo():
  demo_obj = demo()
  return demo_obj.fetch_code_from_repo()
