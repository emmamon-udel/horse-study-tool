
from dataclasses import dataclass
from typing import Optional
from drafter import *


@dataclass
class BodyPart:
    """Represent a horse body part and its related study information."""
    name: str
    category: str
    common_injuries: list[str]
    studied: bool


@dataclass
class State:
    """Keep track of the website's information."""
    body_parts: list[BodyPart]
    current_part: str
    user_answer: str
    feedback: str
    score: int


def make_starting_state() -> State:
    """Create the starting state and a small set of horse anatomy records."""
    parts = [
        BodyPart(
            "Coffin bone",
            "Bone",
            ["fracture", "coffin bone fracture", "pedal bone fracture"],
            False
        ),
        BodyPart(
            "Femur",
            "Bone",
            ["fracture", "femur fracture"],
            False
        ),
        BodyPart(
            "Gluteal muscle",
            "Muscle",
            ["strain", "muscle strain", "muscle tear"],
            False
        ),
        BodyPart(
            "Hoof",
            "External body part",
            ["hoof abscess", "abscess", "hoof bruise", "hoof crack"],
            False
        ),
        BodyPart(
            "Heart",
            "Organ",
            ["heart murmur", "arrhythmia", "cardiac arrhythmia"],
            False
        ),
        BodyPart(
            "Lungs",
            "Organ",
            ["pneumonia", "respiratory infection", "heaves"],
            False
         )
    ]

    return State(
        body_parts=parts,
        current_part="",
        user_answer="",
        feedback="Welcome! Choose a body part to begin studying.",
        score=0
    )


def find_body_part(body_parts: list[BodyPart],
                   part_name: str) -> Optional[BodyPart]:
    """Find a body part by name, ignoring capitalization and extra spaces."""
    for part in body_parts:
        if part.name.lower() == part_name.strip().lower():
            return part
    return None


def normalize_answer(answer: str) -> str:
    """Normalize an answer so capitalization and extra spaces do not matter."""
    return " ".join(answer.strip().lower().split())


def is_correct_injury(part: BodyPart, answer: str) -> bool:
    """Return whether the answer matches one of the accepted injuries."""
    cleaned_answer = normalize_answer(answer)
    
    for accepted_answer in part.common_injuries:
        if cleaned_answer == normalize_answer(accepted_answer):
            return True

    return False


@route
def index(state: State) -> Page:
    """Show the home page and the main navigation options."""
    return Page(state, [
        Header("Horse Anatomy Study Tool"),
        "Learn horse anatomy by practicing recall.",
        "Search for a horse body part, learn its category, and then "
        "answer a question about a common injury.",
        "Current score: " + str(state.score),
        Button("Start studying", "study"),
        Button("Review studied parts", "review"),
        Button("Reset progress", "reset")
    ])


@route
def study(state: State) -> Page:
    """Show a form where the user can enter a horse body-part name."""
    return Page(state, [
        Header("Study a Body Part"),
        "Enter a body-part name from the study list.",
        "Examples: Coffin bone, Femur, Gluteal muscle, Hoof, Heart, Lungs",
        "Body-part name:",
        TextBox("part_name"),
        Button("Search", "identify_part"),
        Button("Home", "index"),
        state.feedback
    ])

@route
def identify_part(state: State, part_name: str) -> Page:
    """Search the BodyPart list and open the matching details page."""
    if part_name.strip() == "":
        state.feedback = "Please enter a body-part name."
        return study(state)

    found_part = None

    for part in state.body_parts:
        if part.name.lower() == part_name.strip().lower():
            found_part = part

    if found_part is not None:
        state.current_part = found_part.name
        state.user_answer = ""
        state.feedback = "Body part found."
        return part_details(state, found_part.name)

    state.current_part = ""
    state.feedback = (
        "That body part was not found. Check the spelling or try "
        "one of the examples on this page."
    )
    return study(state)


@route
def part_details(state: State, part_name: str) -> Page:
    """Display the selected body part's name and category."""
    part = find_body_part(state.body_parts, part_name)

    if part is None:
        state.feedback = "That body part could not be found."
        return study(state)

    state.current_part = part.name
    part.studied = True

    return Page(state, [
        Header("Body Part Details"),
        "Body part: " + part.name,
        "Category: " + part.category,
        "This page identifies the category of the body part. ",
        Button(
            "Take the injury quiz",
            "injury_quiz",
            {"part_name": part.name}
        ),
        Button("Study another body part", "study"),
        Button("Review studied parts", "review"),
        Button("Home", "index")
    ])


@route
def injury_quiz(state: State, part_name: str) -> Page:
    """Ask the user to name a common injury associated with the body part."""
    part = find_body_part(state.body_parts, part_name)

    if part is None:
        state.feedback = "Choose a valid body part before starting the quiz."
        return study(state)

    state.current_part = part.name

    return Page(state, [
        Header("Injury Quiz"),
        "Body part: " + part.name,
        "Name one common injury or condition associated with this part.",
        TextBox("answer"),
        Button(
            "Check answer",
            "check_injury",
            {"part_name": part.name}
        ),
        Button(
            "Back to body-part details",
            "part_details",
            {"part_name": part.name}
        ),
        Button("Home", "index")
    ])

@route
def check_injury(state: State, part_name: str, answer: str) -> Page:
    """Check the submitted injury answer and update score and feedback."""
    state.user_answer = answer
    part = find_body_part(state.body_parts, part_name)

    if part is None:
        state.feedback = "The selected body part could not be found."
        return results(state)

    if answer.strip() == "":
        state.feedback = "You did not enter an answer. Please try again."
        return injury_quiz(state, part.name)

    if is_correct_injury(part, answer):
        state.score = state.score + 1
        state.feedback = "Correct! Your answer was accepted."
    else:
        accepted_answers = ", ".join(part.common_injuries)
        state.feedback = (
            "Not quite. Examples of accepted answers include: "
            + accepted_answers
        )

    return results(state)


@route
def results(state: State) -> Page:
    """Display the answer feedback and the user's current score."""
    return Page(state, [
        Header("Quiz Results"),
        state.feedback,
        "Current score: " + str(state.score),
        Button(
            "Study this body part again",
            "part_details",
            {"part_name": state.current_part}
        ),
        Button("Study another body part", "study"),
        Button("Review studied parts", "review"),
        Button("Home", "index")
    ])

@route
def review(state: State) -> Page:
    """List the body parts that the user has studied during this session."""
    studied_parts = []

    for part in state.body_parts:
        if part.studied:
            studied_parts.append(part.name + " (" + part.category + ")")

    if len(studied_parts) == 0:
        return Page(state, [
            Header("Study Review"),
            "You have not studied any body parts yet.",
            "Choose an option below:",
            SelectBox(
                "review_action",
                ["Continue reviewing", "Reset progress"],
                "Continue reviewing"
            ),
            Button("Submit choice", "handle_review_choice"),
            Button("Start studying", "study"),
            Button("Home", "index")
        ])

    return Page(state, [
        Header("Study Review"),
        "Body parts you have studied:",
        BulletedList(studied_parts),
        "Current score: " + str(state.score),
        "Choose whether to continue studying or reset your progress:",
        SelectBox(
            "review_action",
            ["Continue reviewing", "Reset progress"],
            "Continue reviewing"
        ),
        Button("Submit choice", "handle_review_choice"),
        Button("Study another part", "study"),
        Button("Home", "index")
    ])


@route
def handle_review_choice(state: State, review_action: str) -> Page:
    """Continue to studying or reset progress based on the SelectBox choice."""
    if review_action == "Reset progress":
        return reset(state)

    state.feedback = "You can continue studying another body part."
    return study(state)


@route
def reset(state: State) -> Page:
    """Reset the score and mark every body part as not yet studied."""
    for part in state.body_parts:
        part.studied = False

    state.current_part = ""
    state.user_answer = ""
    state.feedback = "Your study progress has been reset."
    state.score = 0

    return index(state)


def run_tests() -> None:
    """Test helper functions and the website routes."""
    test_state = make_starting_state()

    # Helper function tests
    hoof = find_body_part(test_state.body_parts, "hoof")
    assert hoof is not None
    assert hoof.name == "Hoof"
    assert is_correct_injury(hoof, "ABScess")
    assert not is_correct_injury(hoof, "broken leg")
    assert normalize_answer("  Hoof   Abscess ") == "hoof abscess"

    # Route tests
    assert index(test_state).state.score == 0
    assert study(test_state).state.score == 0

    search_state = make_starting_state()
    search_page = identify_part(search_state, "Hoof")
    assert search_page.state.current_part == "Hoof"
    assert find_body_part(search_state.body_parts, "Hoof").studied

    details_state = make_starting_state()
    details_page = part_details(details_state, "Femur")
    assert details_page.state.current_part == "Femur"
    assert find_body_part(details_state.body_parts, "Femur").studied

    quiz_state = make_starting_state()
    quiz_page = injury_quiz(quiz_state, "Hoof")
    assert quiz_page.state.current_part == "Hoof"

    answer_state = make_starting_state()
    answer_page = check_injury(answer_state, "Hoof", "abscess")    
    assert answer_page.state.score == 1
    assert "Correct" in answer_page.state.feedback

    results_state = make_starting_state()
    results_state.feedback = "Test feedback"
    assert results(results_state).state.feedback == "Test feedback"

    review_state = make_starting_state()
    find_body_part(review_state.body_parts, "Heart").studied = True
    review_page = review(review_state)
    assert review_page.state.body_parts[4].studied

    choice_state = make_starting_state()
    choice_page = handle_review_choice(choice_state, "Continue reviewing")
    assert choice_page.state.feedback == (
        "You can continue studying another body part."
    )

    reset_state = make_starting_state()
    reset_state.score = 4
    reset_state.current_part = "Hoof"
    find_body_part(reset_state.body_parts, "Hoof").studied = True
    reset_page = reset(reset_state)
    assert reset_page.state.score == 0
    assert reset_page.state.current_part == ""
    assert not find_body_part(reset_state.body_parts, "Hoof").studied


# Run tests before starting the website.
run_tests()

set_site_information(
    "Emma Monaghan",
    "An educational website for studying horse anatomy and common injuries.",
    (
        "The website uses a text-based study list. It identifies body-part "
        "categories and quizzes users on common injuries or conditions."
    ),
    "Upload your Final Project 0 and Final Project 1 worksheets "
    "to this repository.",
    ["Replace this with your public GitHub repository URL"]
)
set_website_title("Horse Anatomy Study Tool")


start_server(make_starting_state())
