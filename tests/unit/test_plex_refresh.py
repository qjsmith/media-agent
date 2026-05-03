from unittest.mock import MagicMock, patch

from agent.tools.plex_refresh import refresh_plex_library


def make_mock_server(sections):
    """Helper — returns a mock PlexServer with given library sections."""
    mock_server = MagicMock()
    mock_server.library.sections.return_value = sections
    return mock_server


def test_refresh_calls_update_on_all_sections():
    section1 = MagicMock()
    section2 = MagicMock()

    with patch("agent.tools.plex_refresh.PlexServer", return_value=make_mock_server([section1, section2])):
        result = refresh_plex_library("http://localhost:32400", "fake-token")

    assert result is True
    section1.update.assert_called_once()
    section2.update.assert_called_once()


def test_refresh_returns_true_on_success():
    with patch("agent.tools.plex_refresh.PlexServer", return_value=make_mock_server([MagicMock()])):
        result = refresh_plex_library("http://localhost:32400", "fake-token")

    assert result is True


def test_refresh_returns_false_on_failure():
    with patch("agent.tools.plex_refresh.PlexServer", side_effect=Exception("Connection refused")):
        result = refresh_plex_library("http://localhost:32400", "fake-token")

    assert result is False


def test_refresh_handles_empty_library():
    with patch("agent.tools.plex_refresh.PlexServer", return_value=make_mock_server([])):
        result = refresh_plex_library("http://localhost:32400", "fake-token")

    assert result is True
