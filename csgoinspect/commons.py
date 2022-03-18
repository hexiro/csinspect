import re

INSPECT_LINK_QUERY = '"steam://rungame/730" "+csgo_econ_action_preview"'
INSPECT_URL_REGEX = re.compile(
    "(steam://rungame/730/[0-9]+/(?:\\+| )csgo_econ_action_preview(?:%20| ))(?:(?P<S>S[0-9]+)|(?P<M>M[0-9]+))(?P<A>A[0-9]+)(?P<D>D[0-9]+)"
)
