import json

from app.services import geocoding


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self):
        return self.payload


def test_reverse_geocode_resolves_indian_locality_and_caches(monkeypatch):
    requests = []
    geocoding._reverse_geocode_cached.cache_clear()
    monkeypatch.setattr(geocoding, "_last_reverse_request", 0.0)
    monkeypatch.setattr(geocoding.time, "sleep", lambda delay: None)

    def open_request(request, timeout):
        requests.append((request.full_url, request.headers, timeout))
        return FakeResponse({
            "address": {
                "neighbourhood": "T. Nagar", "postcode": "600017", "country_code": "in",
            },
            "display_name": "T. Nagar, Chennai, Tamil Nadu, India",
        })

    monkeypatch.setattr(geocoding.urllib.request, "urlopen", open_request)
    first = geocoding.reverse_geocode_coordinates(13.041801, 80.233701)
    second = geocoding.reverse_geocode_coordinates(13.041802, 80.233702)

    assert first == second
    assert first["locality"] == "T. Nagar"
    assert first["pincode"] == "600017"
    assert len(requests) == 1
    assert "reverse?" in requests[0][0]
    assert "UtopiaMunicipalPlatform" in requests[0][1]["User-agent"]
    assert requests[0][2] == 5.0


def test_reverse_geocode_does_not_return_non_indian_postcode(monkeypatch):
    geocoding._reverse_geocode_cached.cache_clear()
    monkeypatch.setattr(geocoding, "_last_reverse_request", 0.0)
    monkeypatch.setattr(geocoding.time, "sleep", lambda delay: None)
    monkeypatch.setattr(geocoding.urllib.request, "urlopen", lambda *args, **kwargs: FakeResponse({
        "address": {"city": "London", "postcode": "SW1A 1AA", "country_code": "gb"},
    }))

    result = geocoding.reverse_geocode_coordinates(51.501, -0.141)
    assert result == {"locality": "London", "pincode": None, "lat": 51.501, "lng": -0.141}
