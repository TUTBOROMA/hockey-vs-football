from datetime import datetime

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}
