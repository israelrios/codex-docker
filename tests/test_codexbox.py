import importlib.util
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "codexbox"
LOADER = SourceFileLoader("codexbox_script", str(MODULE_PATH))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load module from {MODULE_PATH}")
CODEXBOX = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CODEXBOX
SPEC.loader.exec_module(CODEXBOX)


class HostPodmanStoreTests(unittest.TestCase):
    def test_prefers_driver_specific_imagestore_over_graph_root(self) -> None:
        store = CODEXBOX.host_podman_store(
            {
                "store": {
                    "graphDriverName": "overlay",
                    "graphRoot": "/var/lib/containers/storage",
                    "graphOptions": {
                        "overlay.imagestore": "/home/test/.local/share/containers/storage",
                    },
                }
            }
        )

        self.assertIsNotNone(store)
        assert store is not None
        self.assertEqual(store.image_store, "/home/test/.local/share/containers/storage")

    def test_falls_back_to_generic_imagestore_key(self) -> None:
        store = CODEXBOX.host_podman_store(
            {
                "store": {
                    "graphDriverName": "btrfs",
                    "graphRoot": "/var/lib/containers/storage",
                    "graphOptions": {
                        "imagestore": "/srv/containers/images",
                    },
                }
            }
        )

        self.assertIsNotNone(store)
        assert store is not None
        self.assertEqual(store.image_store, "/srv/containers/images")

    def test_additional_image_store_uses_effective_image_store_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            home_dir = root / "home"
            graph_root = root / "graph-root"
            image_store = root / "image-store"
            home_dir.mkdir()
            graph_root.mkdir()
            image_store.mkdir()

            additional_store = CODEXBOX.host_podman_additional_image_store(
                {
                    "store": {
                        "graphDriverName": "overlay",
                        "graphRoot": str(graph_root),
                        "graphOptions": {
                            "overlay.imagestore": str(image_store),
                        },
                    }
                },
                home_dir,
                use_fuse_overlayfs=True,
            )

        self.assertEqual(additional_store, str(image_store))


class ForwardedEnvTests(unittest.TestCase):
    def test_repo_ignore_list_does_not_strip_pythonpath(self) -> None:
        patterns = CODEXBOX.load_ignore_patterns(REPO_ROOT / "vars-to-ignore.txt")

        self.assertFalse(CODEXBOX.is_ignored_env_var("PYTHONPATH", patterns))


if __name__ == "__main__":
    unittest.main()
