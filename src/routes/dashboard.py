import ipaddress

from flask import Blueprint, render_template, request

from src.models import Scan, User
from src.routes.decorators import with_user
from src.services.scans import run_scan

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
@with_user
def dashboard_page(user: User):
    return render_template("dashboard.html", username=user.username)


@dashboard_blueprint.post("/scan")
@with_user
def post_scan(user: User):
    form = request.form.to_dict()
    ip_target = valid_ipv4_address(form.get("ipv4"))
    port_target = valid_port(form.get("port"))
    scan: Scan = run_scan(ip_target, port_target, user.id)
    return render_template(
        "result.html", ipv4=ip_target, port=port_target, result=scan.result
    )
