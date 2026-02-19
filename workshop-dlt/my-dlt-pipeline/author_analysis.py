"""
Author Analysis Notebook for Open Library Pipeline
Interactive analytics using marimo, ibis, and matplotlib
"""

import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import dlt
    import ibis
    import matplotlib.pyplot as plt
    import pandas as pd

    return dlt, ibis, mo, plt


@app.cell
def _(dlt):
    # Connect to the dlt pipeline dataset
    pipeline = dlt.pipeline(pipeline_name="open_library_pipeline")
    dataset = pipeline.dataset()
    return (dataset,)


@app.cell
def _(dataset):
    # Get ibis tables - convert Relations to ibis Tables
    books = dataset.table("books").to_ibis()
    books_author_name = dataset.table("books__author_name").to_ibis()
    return books, books_author_name


@app.cell
def _(mo):
    mo.md("""
    # Open Library Author Analysis
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 1. Top 10 Authors by Book Count
    """)
    return


@app.cell
def _(books, books_author_name, dataset, ibis):
    # Count books per author using ibis
    # Join ibis tables
    author_counts_expr = (
        books_author_name
        .join(books, books_author_name._dlt_parent_id == books._dlt_id)
        .group_by(books_author_name.value)
        .aggregate(count=books_author_name._dlt_parent_id.count())
        .order_by(ibis.desc("count"))
        .limit(10)
    )
    
    # Convert expression back to Relation and execute
    author_counts_relation = dataset(author_counts_expr)
    top_authors_df = author_counts_relation.df()
    return (top_authors_df,)


@app.cell
def _(mo):
    # Display table
    mo.md("""
    ### Table: Top 10 Authors
    """)
    return


@app.cell
def _(mo, top_authors_df):
    mo.ui.table(top_authors_df, label="Top 10 Authors")
    return


@app.cell
def _(mo, plt, top_authors_df):
    # Create horizontal bar chart
    fig_authors, ax_authors = plt.subplots(figsize=(10, 6))

    ax_authors.barh(
        top_authors_df["value"].astype(str),
        top_authors_df["count"],
        color="steelblue"
    )
    ax_authors.set_xlabel("Number of Books", fontsize=12)
    ax_authors.set_ylabel("Author", fontsize=12)
    ax_authors.set_title("Top 10 Authors by Book Count", fontsize=14, fontweight="bold")
    ax_authors.invert_yaxis()  # Show top author at the top
    plt.tight_layout()

    mo.md("### Chart: Top 10 Authors")
    return (fig_authors,)


@app.cell
def _(fig_authors, mo):
    mo.mpl.interactive(fig_authors)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 2. Distribution of Publication Years
    """)
    return


@app.cell
def _(books, dataset):
    # Group by publication year
    year_distribution_expr = (
        books
        .filter(~books.first_publish_year.isnull())
        .group_by(books.first_publish_year)
        .aggregate(book_count=books._dlt_id.count())
        .order_by(books.first_publish_year)
    )
    
    # Convert expression back to Relation and execute
    year_distribution_relation = dataset(year_distribution_expr)
    year_dist_df = year_distribution_relation.df()
    return (year_dist_df,)


@app.cell
def _(mo):
    mo.md("""
    ### Table: Books per Publication Year
    """)
    return


@app.cell
def _(mo, year_dist_df):
    mo.ui.table(year_dist_df.head(20), label="Year Distribution (first 20 rows)")
    return


@app.cell
def _(mo, plt, year_dist_df):
    # Create line chart
    fig_years, ax_years = plt.subplots(figsize=(12, 6))

    ax_years.plot(
        year_dist_df["first_publish_year"],
        year_dist_df["book_count"],
        marker="o",
        markersize=3,
        linewidth=1.5,
        color="darkgreen"
    )
    ax_years.set_xlabel("Publication Year", fontsize=12)
    ax_years.set_ylabel("Number of Books", fontsize=12)
    ax_years.set_title("Distribution of Books by Publication Year", fontsize=14, fontweight="bold")
    ax_years.grid(True, alpha=0.3)
    plt.tight_layout()

    mo.md("### Chart: Books per Year")
    return (fig_years,)


@app.cell
def _(fig_years, mo):
    mo.mpl.interactive(fig_years)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 3. Top 10 Authors with Full Text Availability
    """)
    return


@app.cell
def _(books, books_author_name, dataset, ibis):
    # Filter books with full text and count per author
    authors_fulltext_expr = (
        books_author_name
        .join(books, books_author_name._dlt_parent_id == books._dlt_id)
        .filter(books.has_fulltext == True)
        .group_by(books_author_name.value)
        .aggregate(count=books_author_name._dlt_parent_id.count())
        .order_by(ibis.desc("count"))
        .limit(10)
    )
    
    # Convert expression back to Relation and execute
    authors_fulltext_relation = dataset(authors_fulltext_expr)
    authors_fulltext_df = authors_fulltext_relation.df()
    return (authors_fulltext_df,)


@app.cell
def _(mo):
    mo.md("""
    ### Table: Top 10 Authors with Full Text Available
    """)
    return


@app.cell
def _(authors_fulltext_df, mo):
    mo.ui.table(authors_fulltext_df, label="Authors with Full Text")
    return


@app.cell
def _(authors_fulltext_df, mo, plt):
    # Create vertical bar chart
    fig_fulltext, ax_fulltext = plt.subplots(figsize=(10, 6))

    ax_fulltext.bar(
        range(len(authors_fulltext_df)),
        authors_fulltext_df["count"],
        color="coral"
    )
    ax_fulltext.set_xticks(range(len(authors_fulltext_df)))
    ax_fulltext.set_xticklabels(
        authors_fulltext_df["value"].astype(str),
        rotation=45,
        ha="right"
    )
    ax_fulltext.set_xlabel("Author", fontsize=12)
    ax_fulltext.set_ylabel("Number of Books with Full Text", fontsize=12)
    ax_fulltext.set_title("Top 10 Authors with Full Text Availability", fontsize=14, fontweight="bold")
    plt.tight_layout()

    mo.md("### Chart: Authors with Full Text")
    return (fig_fulltext,)


@app.cell
def _(fig_fulltext, mo):
    mo.mpl.interactive(fig_fulltext)
    return


@app.cell
def _(mo):
    mo.md("""
    ## 4. Books per Language
    """)
    return


@app.cell
def _(dataset):
    # Check if books__language table exists
    try:
        books_language = dataset.table("books__language").to_ibis()
        language_exists = True
    except Exception:
        language_exists = False
        books_language = None
    return books_language, language_exists


@app.cell
def _(books, books_language, dataset, ibis, language_exists):
    if language_exists:
        # Count books per language
        language_counts_expr = (
            books_language
            .join(books, books_language._dlt_parent_id == books._dlt_id)
            .group_by(books_language.value)
            .aggregate(count=books_language._dlt_parent_id.count())
            .order_by(ibis.desc("count"))
        )
        
        # Convert expression back to Relation and execute
        language_counts_relation = dataset(language_counts_expr)
        language_counts_df = language_counts_relation.df()
    else:
        language_counts_df = None
    return (language_counts_df,)


@app.cell
def _(language_exists, mo):
    if language_exists:
        mo.md("### Table: Books per Language")
    else:
        mo.md("### Note: Language data not available")
    return


@app.cell
def _(language_counts_df, language_exists, mo):
    if language_exists and language_counts_df is not None:
        mo.ui.table(language_counts_df.head(20), label="Language Distribution (first 20 rows)")
    return


@app.cell
def _(mo):
    mo.md("""
    ### Chart: Books per Language
    """)
    return


@app.cell
def _(language_counts_df, language_exists, plt):
    if language_exists and language_counts_df is not None:
        # Create bar chart
        fig_languages, ax_languages = plt.subplots(figsize=(12, 6))

        # Show top 20 languages
        top_languages = language_counts_df.head(20)

        ax_languages.bar(
            range(len(top_languages)),
            top_languages["count"],
            color="mediumpurple"
        )
        ax_languages.set_xticks(range(len(top_languages)))
        ax_languages.set_xticklabels(
            top_languages["value"].astype(str),
            rotation=45,
            ha="right"
        )
        ax_languages.set_xlabel("Language", fontsize=12)
        ax_languages.set_ylabel("Number of Books", fontsize=12)
        ax_languages.set_title("Books per Language (Top 20)", fontsize=14, fontweight="bold")
        plt.tight_layout()
    else:
        fig_languages = None
    return (fig_languages,)


@app.cell
def _(fig_languages, language_exists, mo):
    if language_exists and fig_languages is not None:
        mo.mpl.interactive(fig_languages)
    return


if __name__ == "__main__":
    app.run()
