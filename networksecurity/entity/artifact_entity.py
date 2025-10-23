from dataclasses import dataclass #acts as a decorater creates variable for an empty class


@dataclass
class DataIngestionArtifact:
    trained_file_path:str
    test_file_path:str