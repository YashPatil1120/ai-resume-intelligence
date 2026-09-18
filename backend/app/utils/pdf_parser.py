import pymupdf


# ==================================================
# PDF TEXT EXTRACTION
# ==================================================

def extract_text_from_pdf(
    pdf_path
):
    """
    Extract text from a text-based PDF.

    Parameters
    ----------
    pdf_path : str
        Path to the PDF file.

    Returns
    -------
    str
        Extracted text.
    """

    document = pymupdf.open(
        pdf_path
    )

    pages = []


    for page in document:

        text = page.get_text()

        if text.strip():

            pages.append(
                text
            )


    document.close()


    return "\n".join(
        pages
    )


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    pdf_path = "data/test_resume.pdf"


    try:

        text = extract_text_from_pdf(
            pdf_path
        )


        print()

        print("Extracted Resume Text")

        print("=====================")

        print()

        print(text)


    except FileNotFoundError:

        print()

        print(
            f"PDF not found: {pdf_path}"
        )

        print(
            "Please place a PDF resume at "
            "that location before running the test."
        )