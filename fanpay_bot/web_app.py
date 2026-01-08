from __future__ import annotations

from collections import defaultdict

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
        query = request.args.get("q", "").strip()
        games = service.list_games(query or None)
        return render_template("index.html", games=games, query=query)

    @app.get("/games/<game_id>")
    def game_detail(game_id: str) -> str:
        games = {game.game_id: game for game in service.list_games()}
        game = games.get(game_id)
        if not game:
            return render_template("not_found.html", message="Игра не найдена."), 404
        categories = service.list_categories(game_id)
        listing_map: dict[str, list] = defaultdict(list)
        for category in categories:
            listing_map[category.category_id] = service.list_listings(game_id, category.category_id)
        return render_template(
            "game_detail.html",
            game=game,
            categories=categories,
            listing_map=listing_map,
        )

    @app.post("/games")
    def create_game() -> str:
        name = request.form.get("name", "").strip()
        if not name:
            return render_template("not_found.html", message="Укажи название игры."), 400
        game = service.create_game(name)
        return redirect(url_for("game_detail", game_id=game.game_id))

    @app.post("/categories")
    def create_category() -> str:
        game_id = request.form.get("game_id", "")
        name = request.form.get("name", "").strip()
        item_type = request.form.get("item_type", "").strip() or None
        if not game_id or not name:
            return render_template("not_found.html", message="Нужны игра и название категории."), 400
        service.create_category(game_id=game_id, name=name, item_type=item_type)
        return redirect(url_for("game_detail", game_id=game_id))

    @app.post("/listings")
    def create_listing() -> str:
        game_id = request.form.get("game_id", "")
        category_id = request.form.get("category_id", "")
        title = request.form.get("title", "").strip()
        price = request.form.get("price", "").strip()
        currency = request.form.get("currency", "RUB").strip() or "RUB"
        quantity = request.form.get("quantity", "1").strip()
        sold_24h = request.form.get("sold_24h", "0").strip()
        if not game_id or not category_id or not title or not price:
            return render_template("not_found.html", message="Заполни все поля объявления."), 400
        service.create_listing(
            game_id=game_id,
            category_id=category_id,
            title=title,
            price=float(price),
            currency=currency,
            quantity=int(quantity or 1),
            sold_24h=int(sold_24h or 0),
        )
        return redirect(url_for("game_detail", game_id=game_id))

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

    return app


def main() -> None:
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)


if __name__ == "__main__":
    main()
