## About test driven development
Test driven development (TDD) means writing tests before writing code. This is done using the Red, Green, Refactor cycle. In the "red" phase, a test is written that fails. The test demonstrates a behaviour that the code does not exhibit yet. In the "green" phase, the code under test is modified just enough to make all the tests pass. In the green phase you're allowed to take shortcuts and the code does not have to be nice yet. After the green phase comes the "refactor" phase. In this phase the code is updated to optimize readability and to make the code good. When all the phases are done, the cycle repeats.

Test driven development is done in pair programming style, so working together with the user is highly encouraged.

## Guidlines when doing test driven development
Keep in mind the following best practices when doing TDD:

- A test should express the behaviour from the perspective of a user. This applies to both the name of the test as well as the content of the test.
- A test should be as explicit as possible about values that are relevant for the current test scenario
- A test should hide as much as possible the values that are not relevant for the current test scenario
- A good test is exactly 3 lines long: one line for given, one for when and one for then. You should aim to get as close to three lines as possible.
- A good test only uses the system under test for the when section. A good test does not use the system under test for the given or then sections.

### During the Red phase
- Always ensure that the test is failing by running the test with the test runner tool
- Compile-time errors are NOT ACCEPTABLE as failure in the red phase. Also module import errors are NOT ACCEPTABLE. Missing method or missing property errors are also NOT ACCEPTABLE.
- Prefer failure on assertions over failure in code under test as much as practical.
- NEVER implement the code before running the test
- ALWAYS make a guess what the expected failure is before running the test
- ALWAYS ask for approval before proceeding to the green phase
- ALWAYS run the test before asking for approval

### During the Green phase
- Make as few changes as possible. It's okay to ignore warnings at this point if that's practical.
- Run the test using the test runner tool and make sure no regressions were introduced.
- When the tests pass, ask for approval to proceed to the refactor phase

### During the Refactor phase
- It's not mandatory to make changes in the refactor phase. Only suggest changes if they make the code easier to change or easier to read
- Suggest changes to the user and always ask for verification before applying a refactor

## Example of a good test
The following code demonstrates the perfect test.

```python
def test_should_greet_user_by_name():
    # given
    user = create_user(name="Eric")

    # when
    result = UserGreeter().create_greet(user)

    # then
    assert "Eric" in result
```

Every test should be as close as possible to this test.