"""
Testbestand voor de Flask webapp (app.py).
Dit bestand test alle webpagina’s van de app.
Er worden geen echte bestanden of mappen gebruikt.
"""

import json
from unittest.mock import mock_open, patch

from web.app import app


def test_index_get():
    """Test of de startpagina (/) gewoon opent."""
    # Start een nep-browser
    with app.test_client() as client:
        # Ga naar de startpagina
        response = client.get("/")
        
    # De pagina moet laden
    assert response.status_code == 200


def test_index_post_creates_job(tmp_path):
    """Test of het uploaden van een bestand een nieuwe job start."""
    # Maak een tijdelijk nep-bestand met DNA-tekst
    fastq_file = tmp_path / "sample.fastq"
    fastq_file.write_text("@SEQ\nACGT\n+\n!!!!\n")

    # Open het bestand en stop het in het formulier
    file_handle = open(fastq_file, "rb")
    post_data = {
        "fastp-paired": "0",
        "fastq-file-r1": file_handle,
    }

    # Zorg dat tijd, mappen en bestanden niet echt worden gebruikt
    with app.test_client() as client, \
         patch("web.app.time.time_ns", return_value=12345), \
         patch("web.app.os.makedirs"), \
         patch("werkzeug.datastructures.FileStorage.save"), \
         patch("web.app.Job.create_commands") as mock_create_commands, \
         patch("web.app.Job.save") as mock_save:
        
        # Stuur het formulier
        response = client.post("/", data=post_data, content_type="multipart/form-data")

    file_handle.close()

    # Check of alles is gedaan
    assert response.status_code == 200
    assert mock_create_commands.called
    assert mock_save.call_count == 2


def test_get_job_status_returns_results():
    """Test of resultaten worden gestuurd als de job klaar is."""
    # Nep-gegevens van een afgeronde job
    results_data = {"job_id": "123", "status": "completed"}
    mocked_file = mock_open(read_data=json.dumps(results_data))

    # Doe alsof dit bestand bestaat
    with app.test_client() as client, \
         patch("web.app.os.path.exists") as mock_exists, \
         patch("builtins.open", mocked_file):
        
        # Alleen het resultatenbestand bestaat
        mock_exists.side_effect = lambda path: path.endswith("_results.json")
        
        # Vraag de status van job 123
        response = client.get("/job/123/status")

    # De juiste data moet terugkomen
    assert response.status_code == 200
    assert response.get_json() == results_data


def test_get_job_status_returns_job_status():
    """Test of de status wordt gestuurd als de job nog bezig is."""
    # Nep-gegevens van een lopende job
    job_data = {"status": "processing"}
    mocked_file = mock_open(read_data=json.dumps(job_data))

    with app.test_client() as client, \
         patch("web.app.os.path.exists") as mock_exists, \
         patch("builtins.open", mocked_file):
        
        # Het job-bestand bestaat, maar geen resultaten
        mock_exists.side_effect = lambda path: path.endswith("_job.json")
        
        # Vraag de status van job 987
        response = client.get("/job/987/status")

    assert response.status_code == 200
    assert response.get_json() == {"job_id": "987", "status": "processing"}


def test_get_job_status_not_found():
    """Test wat er gebeurt als een job niet bestaat."""
    # Doe alsof er geen bestanden zijn
    with app.test_client() as client, patch("web.app.os.path.exists", return_value=False):
        response = client.get("/job/404/status")

    # De app moet zeggen dat de job niet bestaat
    assert response.status_code == 404
    assert response.get_json() == {"error": "Job not found"}


def test_serve_data_invalid_path():
    """Test of foute paden worden tegengehouden."""
    with app.test_client() as client:
        # Probeer buiten de map te komen
        response = client.get("/data/../secret.txt")
        
    assert response.status_code == 403
    assert response.get_json() == {"error": "Invalid path"}


def test_serve_data_file_not_found():
    """Test wat er gebeurt als een bestand niet bestaat."""
    # Doe alsof het bestand er niet is
    with app.test_client() as client, patch("web.app.os.path.exists", return_value=False):
        response = client.get("/data/job1/file.txt")

    # Er moet een foutmelding komen
    assert response.status_code == 404
    assert response.get_json() == {"error": "File not found"}


def test_history_lists_finished_jobs():
    """Test of de geschiedenis alleen jobs laat zien die klaar zijn."""
    # Nep-gegevens van een afgeronde job
    history_data = {
        "status": "done",
        "completed_at": 123456,
        "job_size": 777,
        "fastq_report": "report.html",
        "krona_output": "krona.html",
    }

    # Doe alsof er twee job-mappen zijn
    with app.test_client() as client, \
         patch("web.app.os.listdir", return_value=["job1", "job2"]), \
         patch("web.app.os.path.isdir", return_value=True), \
         patch("web.app.os.path.exists") as mock_exists, \
         patch("builtins.open", mock_open(read_data=json.dumps(history_data))), \
         patch("web.app.render_template", return_value="history-ok") as mock_render:
        
        # Alleen job1 telt mee
        mock_exists.side_effect = lambda path: path.endswith("job1/job1_results.json")
        
        # Ga naar de geschiedenis-pagina
        response = client.get("/history")

    assert response.status_code == 200
    
    # Pak de lijst die naar de pagina ging
    rendered_history = mock_render.call_args.kwargs["history"]
    
    assert len(rendered_history) == 1
    assert rendered_history[0]["job_id"] == "job1"
    assert rendered_history[0]["status"] == "done"
