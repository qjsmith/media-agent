from plexapi.server import PlexServer


def refresh_plex_library(plex_url: str, plex_token: str) -> bool:
    """Trigger a full Plex library refresh. Returns True on success."""
    try:
        server = PlexServer(plex_url, plex_token)
        for library in server.library.sections():
            library.update()
        print("[Plex] Library refresh triggered successfully.")
        return True
    except Exception as e:
        print(f"[Plex] Library refresh failed: {e}")
        return False
