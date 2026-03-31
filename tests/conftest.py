# zorgt ervoor dat de relatieve paden werken in de tests
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "worker")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))