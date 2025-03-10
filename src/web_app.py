from flask import Flask, jsonify, render_template, send_from_directory, request
from core.hardware_manager import HardwareManager
from core.network import Network
import os
from flask_cors import CORS
import logging

# Initialize Flask app with static and template directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
app = Flask(
    __name__,
    static_folder=os.path.join(
        BASE_DIR, "static"
    ),  # Serve CSS/JS files from the static directory
    template_folder=os.path.join(BASE_DIR, "templates"),  # Serve HTML templates
)
CORS(app)
# Define Results directory for downloadable and uploaded files
RESULTS_DIR = os.path.join(BASE_DIR, "Results")

# Ensure Results directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)

hardware_manager = HardwareManager()
network_manager = Network()


@app.route("/")
def index():
    """
    Home Page: Renders the index.html template.
    """
    try:
        return render_template("index.html")
    except Exception as e:
        return render_template("500.html", error=str(e)), 500


@app.route("/api/hardware_summary", methods=["GET"])
def hardware_summary():
    """
    API Endpoint: Fetch hardware summary.
    """
    try:
        manager = HardwareManager()
        summary = manager.get_hardware_summary()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch hardware summary: {str(e)}"}), 500


@app.route("/api/network_summary", methods=["GET"])
def network_summary():
    """
    API Endpoint: Fetch network summary.
    """
    try:
        network = Network()
        summary = network.to_dict()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch network summary: {str(e)}"}), 500


@app.route("/api/device_status", methods=["GET"])
def device_status():
    """
    API Endpoint: Check the status of connected devices.
    """
    try:
        devices = HardwareManager().get_device_status()
        return jsonify(devices), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch device status: {str(e)}"}), 500


@app.route("/results/<filename>", methods=["GET"])
def download_file(filename):
    """
    Serve files from the Results directory.
    """
    try:
        return send_from_directory(RESULTS_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": f"File '{filename}' not found."}), 404


@app.route("/upload_results", methods=["POST"])
def upload_results():
    """
    Endpoint to handle file uploads to the Results directory.
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        save_path = os.path.join(RESULTS_DIR, file.filename)
        file.save(save_path)
        return (
            jsonify({"message": f"File '{file.filename}' uploaded successfully"}),
            201,
        )
    except Exception as e:
        return jsonify({"error": f"File upload failed: {str(e)}"}), 500


@app.route("/api/generate_report", methods=["POST"])
def generate_report():
    """
    Endpoint to generate a report combining hardware and network summaries.
    """
    try:
        manager = HardwareManager()
        network = Network()
        hardware_summary = manager.get_hardware_summary()
        network_summary = network.to_dict()

        combined_summary = {
            "hardware_summary": hardware_summary,
            "network_summary": network_summary,
        }

        report_path = os.path.join(RESULTS_DIR, "combined_report.json")
        with open(report_path, "w") as report_file:
            report_file.write(json.dumps(combined_summary, indent=4))

        return (
            jsonify(
                {
                    "message": "Report generated successfully",
                    "report_url": f"/results/combined_report.json",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": f"Report generation failed: {str(e)}"}), 500


@app.route("/api/hardware")
def get_hardware():
    try:
        return jsonify(hardware_manager.get_hardware_summary())
    except Exception as e:
        logging.error(f"Hardware API error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/network")
def get_network():
    try:
        return jsonify(network_manager.get_network_summary())
    except Exception as e:
        logging.error(f"Network API error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/monitoring")
def get_monitoring():
    try:
        return jsonify(
            {
                "cpu_usage": hardware_manager.get_cpu_usage(),
                "ram_usage": hardware_manager.get_ram_usage(),
                "gpu_usage": hardware_manager.get_gpu_usage(),
            }
        )
    except Exception as e:
        logging.error(f"Monitoring API error: {e}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def page_not_found(e):
    """
    Custom 404 error handler.
    """
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    """
    Custom 500 error handler.
    """
    error_message = str(e) or "An internal server error occurred."
    return render_template("500.html", error=error_message), 500


if __name__ == "__main__":
    # Enable access on all network interfaces for mobile and web clients
    app.run(host="0.0.0.0", port=5000, debug=True)
