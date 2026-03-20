from backend.extractors.pdf import PDFExtractor
from backend.extractors.arxiv import ArxivExtractor
from backend.extractors.pubmed import PubMedExtractor
from backend.extractors.biorxiv import BioRxivExtractor
from backend.extractors.youtube import YouTubeExtractor
from backend.extractors.github import GitHubExtractor
from backend.extractors.clinical_trials import ClinicalTrialsExtractor
from backend.extractors.generic import GenericWebExtractor

__all__ = [
    "PDFExtractor",
    "ArxivExtractor",
    "PubMedExtractor",
    "BioRxivExtractor",
    "YouTubeExtractor",
    "GitHubExtractor",
    "ClinicalTrialsExtractor",
    "GenericWebExtractor",
]
