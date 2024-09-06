import subprocess
from io import StringIO
from dotenv import load_dotenv
import os

result = subprocess.run(["azd","env","get-values"], stdout=subprocess.PIPE, cwd=os.getcwd())
print(result)