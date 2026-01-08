from __future__ import annotations

from flask import Flask, redirect, render_template, request, url_for

from fanpay_bot.config import load_config
from fanpay_bot.service import FanPayService


def create_app() -> Flask:
    app = Flask(__name__)
    config = load_config()
    service = FanPayService.from_config(
        data_source=config.data_source,
        sample_data_path=config.sample_data_path,
        sqlite_path=config.sqlite_path,
    )

    @app.get("/")
    def index() -> str:
        games = service.list_games()
        return render_template("index.html", games=games)

    @app.get("/games/<game_id>")
    def game_detail(game_id: str) -> str:
        games = {game.game_id: game for game in service.list_games()}
        game = games.get(game_id)
        if not game:
            return render_template("not_found.html", message="Игра не найдена."), 404
        categories = service.list_categories(game_id)
        return render_template("game_detail.html", game=game, categories=categories)

    @app.post("/snapshot")
    def snapshot() -> str:
        game_id = request.form.get("game_id", "")
        category_ids = request.form.getlist("category_ids")
        if not game_id or not category_ids:
            return render_template("not_found.html", message="Нужны игра и категории."), 400
        result = service.capture_snapshot(game_id, category_ids)
        return render_template(
            "snapshot_result.html",
            game_id=game_id,
            total_listings=result.total_listings,
        )

    @app.post("/analyze")
    def analyze() -> str:
        game_id = request.form.get("game_id", "")
        category_ids = request.form.getlist("category_ids")
        if not game_id or not category_ids:
            return render_template("not_found.html", message="Нужны игра и категории."), 400
        try:
            reports = service.analyze_categories(game_id, category_ids)
        except RuntimeError as exc:
            return render_template("not_found.html", message=str(exc)), 400
        return render_template(
            "analysis.html",
            reports=reports,
            game_id=game_id,
        )

    @app.post("/refresh")
    def refresh() -> str:
        return redirect(url_for("index"))

    return app


def main() -> None:
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)


if __name__ == "__main__":
    main()
