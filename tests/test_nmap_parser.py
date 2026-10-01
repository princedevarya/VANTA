from app.services.parsers.nmap import parse_nmap_output


def test_parse_nmap_output():
    output = """
    Starting Nmap 7.99

    Nmap scan report for example.com (93.184.216.34)

    PORT     STATE SERVICE
    80/tcp   open  http
    443/tcp  open  https
    8080/tcp open  http
    """

    result = parse_nmap_output(output)

    assert result["host"] == "example.com"

    assert len(result["services"]) == 3

    assert result["services"][0] == {
        "port": 80,
        "protocol": "tcp",
        "state": "open",
        "service": "http",
    }

    assert result["services"][1]["port"] == 443
    assert result["services"][2]["port"] == 8080


def test_parse_nmap_empty_output():
    result = parse_nmap_output("")

    assert result["host"] is None
    assert result["services"] == []