import os


def test_publication_folder_structure() -> None:
    required_dirs = [
        "publications/shared/references",
        "publications/shared/author_guidelines",
        "publications/shared/experts",
        "publications/shared/templates",
        "publications/P1_Qualitative_MJA/01_Protocol",
        "publications/P1_Qualitative_MJA/02_Analysis",
        "publications/P1_Qualitative_MJA/03_Manuscript",
        "publications/P1_Qualitative_MJA/04_Submission",
        "publications/P2_Modelling_MJA/01_Protocol",
        "publications/P2_Modelling_MJA/02_Analysis",
        "publications/P2_Modelling_MJA/03_Manuscript",
        "publications/P2_Modelling_MJA/04_Submission",
        "publications/P3_RACMA_Position/01_Drafting",
        "publications/P3_RACMA_Position/02_Final",
    ]

    for d in required_dirs:
        assert os.path.isdir(d), f"Directory missing: {d}"


if __name__ == "__main__":
    test_publication_folder_structure()
    print("All publication directories verified.")
