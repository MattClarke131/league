# -*- coding: utf-8 -*-
"""Dashboard."""
from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import login_required, login_user

from league.dashboard.forms import (GameCreateForm, PlayerCreateForm,
                                    PlayerDeleteForm, ReportGenerateForm)
from league.dashboard.reports import Report
from league.extensions import csrf_protect
from league.models import Game, Player
from league.public.forms import LoginForm
from league.utils import flash_errors

blueprint = Blueprint('dashboard', __name__, url_prefix='/dashboard',
                      static_folder='../static')


@blueprint.route('/', methods=['GET', 'POST'])
def dashboard():
    """Dashboard."""
    site_settings = current_app.config['SITE_SETTINGS']
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash('You are logged in.', 'success')
            redirect_url = (request.args.get('next') or
                            url_for('dashboard.dashboard'))
            return redirect(redirect_url)
        else:
            flash_errors(form)
    players = Player.query.all()
    games = Game.query.all()
    return render_template('dashboard/dashboard.html',
                           site_settings=site_settings,
                           login_form=form,
                           players=players, games=games,
                           episode_stats=Game.episode_stats())


@blueprint.route('/prizes/', methods=['GET', 'POST'])
def prizes():
    """Prizes and achievements."""
    site_settings = current_app.config['SITE_SETTINGS']
    players = Player.query.all()
    games = Game.query.all()
    return render_template('dashboard/prizes.html', site_settings=site_settings,
                           players=players, games=games,
                           season_stats=Game.season_stats())


@blueprint.route('/players/', methods=['GET'])
@login_required
def get_players():
    """Get list of players."""
    form = PlayerCreateForm(request.form)
    players = Player.query.all()
    return render_template('dashboard/players.html', players=players,
                           player_create_form=form)


@blueprint.route('/players/', methods=['POST'])
@login_required
def create_player():
    """Create a new player."""
    form = PlayerCreateForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        Player.create(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            aga_id=form.aga_id.data,
            aga_rank=form.aga_rank.data
        )
        flash('Player created!', 'success')
    else:
        flash_errors(form)
    players = Player.query.all()
    return render_template('dashboard/players.html', players=players,
                           player_create_form=form)


@blueprint.route('/players/<int:player_id>', methods=['GET'])
def get_player(player_id):
    """Get game history and statistics for player."""
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash('You are logged in.', 'success')
            redirect_url = request.args.get('next') or url_for('public.home')
            return redirect(redirect_url)
        else:
            flash_errors(form)

    player = Player.get_by_id(player_id)

    return render_template(
        'dashboard/player.html',
        player=player,
        episode_stats=player.episode_stats(),
        season_stats=player.season_stats(),
        league_stats=player.league_stats(),
        login_form=form
    )


@blueprint.route('/players/delete/', methods=['POST'])
@login_required
def delete_player():
    """Delete a player."""
    form = PlayerDeleteForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        Player.delete(Player.get_by_id(form.player_id.data))
        flash('Player deleted!', 'success')
    else:
        flash_errors(form)
    return redirect(url_for('dashboard.get_players'))


def _set_game_create_choices(game_create_form):
    """
    Calculate choices for season and episode and update form.

    Should allow up to one more than current maxima.
    """
    max_season, max_episode = Game.get_max_season_ep()
    game_create_form.season.choices = [(s, s) for s in range(1, max_season + 2)]
    game_create_form.episode.choices = [(e, e) for e in
                                        range(1, max_episode + 2)]

    player_choices = [
        (player.id, '{} ({})'.format(player.full_name, player.aga_id))
        for player in Player.get_players()
    ]
    game_create_form.white_id.choices = player_choices
    game_create_form.black_id.choices = player_choices


@blueprint.route('/games/', methods=['GET'])
@login_required
def list_games():
    """Get list of games."""
    form = GameCreateForm(request.form, csrf_enabled=False)
    _set_game_create_choices(form)

    games = Game.query.all()
    return render_template('dashboard/games.html', games=games,
                           game_create_form=form)


@blueprint.route('/games/<int:game_id>', methods=['DELETE'])
@login_required
@csrf_protect.exempt
def delete_game(game_id):
    """Delete a game."""
    game = Game.get_by_id(game_id)
    if game is not None:
        game.delete()
        return '', 204
    else:
        return '', 404


@blueprint.route('/reports/', methods=['GET'])
@login_required
def get_reports():
    """Get reports page."""
    form = ReportGenerateForm(request.form, csrf_enabled=False)
    return render_template('dashboard/reports.html', report_generate_form=form)


@blueprint.route('/reports/', methods=['POST'])
@login_required
def generate_report():
    """Generate results report for submission to AGA."""
    form = ReportGenerateForm(request.form, csrf_enabled=False)
    report = None
    if form.validate_on_submit():
        report = Report(form.season.data, form.episode.data)
    else:
        flash_errors(form)
    return render_template('dashboard/reports.html', report=report,
                           report_generate_form=form)
