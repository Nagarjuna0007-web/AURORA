from app.core.logger import logger

try:
    a = int(input("Enter first number: "))
    b = int(input("Enter second number: "))

    result = a / b

    print("Result:", result)

except ValueError:
    logger.error("Please enter valid integers.")

except ZeroDivisionError:
    logger.exception("Cannot divide by zero.")

except Exception as e:
    logger.exception(f"Unexpected error: {e}")

else:
    logger.info("Division completed successfully.")

finally:
    print("Program finished.")