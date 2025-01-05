from typing import List, Optional
from dataclasses import dataclass, field

from util.util import log


@dataclass
class Season:
  air_date: Optional[str] = None
  episode_count: Optional[int] = None
  id: Optional[int] = None
  name: Optional[str] = None
  overview: Optional[str] = None
  poster_path: Optional[str] = None
  season_number: Optional[int] = None
  vote_average: Optional[float] = None

  @staticmethod
  def from_dict(data: dict) -> "Season":
    return Season(
        air_date=data.get("air_date"),
        episode_count=data.get("episode_count"),
        id=data.get("id"),
        name=data.get("name"),
        overview=data.get("overview"),
        poster_path=data.get("poster_path"),
        season_number=data.get("season_number"),
        vote_average=data.get("vote_average"),
    )


@dataclass
class Show:
  id: Optional[int] = None
  backdrop_path: Optional[str] = None
  first_air_date: Optional[str] = None
  last_air_date: Optional[str] = None
  name: Optional[str] = None
  number_of_episodes: Optional[int] = None
  number_of_seasons: Optional[int] = None
  origin_country: List[str] = field(default_factory=list)
  original_language: Optional[str] = None
  original_name: Optional[str] = None
  overview: Optional[str] = None
  popularity: Optional[float] = None
  poster_path: Optional[str] = None
  seasons: List[Season] = field(default_factory=list)
  status: Optional[str] = None
  vote_average: Optional[float] = None
  vote_count: Optional[int] = None

  @staticmethod
  def from_dict(data: dict) -> "Show":
    return Show(
        id=data.get("id"),
        backdrop_path=data.get("backdrop_path"),
        first_air_date=data.get("first_air_date"),
        last_air_date=data.get("last_air_date"),
        name=data.get("name"),
        number_of_episodes=data.get("number_of_episodes"),
        number_of_seasons=data.get("number_of_seasons"),
        origin_country=data.get("origin_country", []),
        original_language=data.get("original_language"),
        original_name=data.get("original_name"),
        overview=data.get("overview"),
        popularity=data.get("popularity"),
        poster_path=data.get("poster_path"),
        seasons=[Season.from_dict(season) for season in
                 data.get("seasons", [])],
        status=data.get("status"),
        vote_average=data.get("vote_average"),
        vote_count=data.get("vote_count"),
    )

  def get_season(self, season_number):
    if season_number < 0 or season_number > self.number_of_seasons:
      return None
    for season in self.seasons:
      if season.season_number == season_number:
        return season

  def get_back_button_episode(self, current_season, current_ep):
    current_season = int(current_season)
    current_ep = int(current_ep)
    if current_ep > 1:
      return current_season, current_ep - 1
    previous_season = self.get_season(current_season - 1)
    if not previous_season:
      log(f'Season {current_season} has no previous')
      return None, None

    return current_season - 1, int(previous_season.episode_count)

  def get_next_button_episode(self, current_season_number, current_ep):
    current_season_number = int(current_season_number)
    current_ep = int(current_ep)
    current_season = self.get_season(current_season_number)
    if current_ep < current_season.episode_count:
      log(f'Next button S{current_season_number} ep {current_ep + 1}')
      return current_season_number, current_ep + 1

    next_season = self.get_season(current_season_number + 1)
    if not next_season:
      log(f'Season {current_season_number} has no next')
      return None, None

    return current_season_number + 1, 1
