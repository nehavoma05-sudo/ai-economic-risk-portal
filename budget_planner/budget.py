CURRENT_INFLATION = 3.48
from .rise_cal import predict_next_month_impact

def calculate_budget_plan(user_input):
    prediction=predict_next_month_impact()
    petrol_extra = (
        user_input.get("petrol_liters", 0)
        * prediction.get("petrol_rise", 0)
    )

    diesel_extra = (
        user_input.get("diesel_liters", 0)
        * prediction.get("diesel_rise", 0)
    )

    lpg_extra = (
        user_input.get("lpg_cylinders", 0)
        * prediction.get("lpg_rise", 0)
    )

    predicted_inflation = prediction.get("inflation_percent", 0)
    inflation_change = max(0, predicted_inflation - CURRENT_INFLATION)

    groceries_extra = (
        user_input.get("groceries_cost", 0)
        * inflation_change / 100
    )

    electricity_extra = (
        user_input.get("electricity_cost", 0)
        * inflation_change / 100
    )

    medical_extra = (
        user_input.get("medical_cost", 0)
        * inflation_change / 100
    )

    total_extra_cost = (
        petrol_extra
        + diesel_extra
        + lpg_extra
        + groceries_extra
        + electricity_extra
        + medical_extra
    )

    recommended_budget = (
        user_input.get("monthly_budget", 0)
        + total_extra_cost
    )

    return {
    "petrol_extra_cost": round(petrol_extra, 2),
    "diesel_extra_cost": round(diesel_extra, 2),
    "lpg_extra_cost": round(lpg_extra, 2),
    "groceries_extra_cost": round(groceries_extra, 2),
    "electricity_extra_cost": round(electricity_extra, 2),
    "medical_extra_cost": round(medical_extra, 2),

    "budget_summary": {
        "current_monthly_budget": round(
            user_input.get("monthly_budget", 0), 2
        ),
        "recommended_next_month_budget": round(
            recommended_budget, 2
        ),
        "additional_budget_required": round(
            total_extra_cost, 2
        )
    }
}

if __name__ == "__main__":
    sample_input = {
        "monthly_budget": 50000,
        "petrol_liters": 100,
        "diesel_liters": 50,
        "lpg_cylinders": 2,
        "groceries_cost": 15000,
        "electricity_cost": 3000,
        "medical_cost": 2000
    }
    result = calculate_budget_plan(sample_input)
    print(result)