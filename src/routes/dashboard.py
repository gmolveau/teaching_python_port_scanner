import ipaddress

from flask import Blueprint, render_template, request

from src.core.scan import scan
from src.services.sessions import login_required

dashboard_blueprint = Blueprint("dashboard", __name__)


def valid_ipv4_address(value):
    try:
        ipaddress.IPv4Address(value)
        return value
    except ipaddress.AddressValueError:
        raise ValueError(f"{value} is not a valid IPv4 address.")


def valid_port(value):
    try:
        port = int(value)
    except ValueError:
        raise ValueError(f"{value} is not a valid integer.")

    if not (0 <= port <= 65535):
        raise ValueError(f"{port} is not a valid port number (0-65535).")
    return port


@dashboard_blueprint.get("/dashboard")
@login_required
def dashboard_page():
    return render_template("dashboard.html")


@dashboard_blueprint.post("/scan")
@login_required
def post_scan():
    form = request.form.to_dict()
    ip_target = valid_ipv4_address(form.get("ipv4"))
    port_target = valid_port(form.get("port"))
    result = scan(ip_target, port_target)
    return render_template(
        "result.html", ipv4=ip_target, port=port_target, result=result
    )
