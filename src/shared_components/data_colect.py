from tokenize import String
from bs4 import BeautifulSoup
import requests
from src.shared_components import values

def get_title_and_hyperlinks_from_af(url_af=values.URL_AF_RELEASES, headers=values.HEADERS, extract_amount=10, start_page=1, extract_dub=False, print_log=False):
    """
    Extracts text and hyperlinks from a web page.

    Args:
    - url_af: URL of the AnimeFire releases page.
    - headers: Headers to use for the HTTP request.
    - extract_amount: Number of links to extract.
    - start_page: Page number to start extraction from.
    - extract_dub: Boolean indicating whether to include dubbed links.
    - print_log: Boolean indicating whether to print log messages.

    Returns:
    - List of tuples containing title and hyperlink from the release page of Anime Fire.
    """
    results = []
    page = start_page
    hard_limit = 100
    extract_amount = min(extract_amount, hard_limit)  # Apply hard limit

    while len(results) < extract_amount:
        current_url = url_af.replace("/1", f"/{page}")
        response = requests.get(current_url, headers=headers)
        try:
            response.raise_for_status()  # Check if there was an error in the request
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')
            BASE_URL = values.URL_AF_FILTER_RELEAES

            for link in links:
                href = link.get('href')
                text = link.get_text()
                if href and BASE_URL in href:
                    if not extract_dub and "(Dublado)" in text:
                        continue
                    results.append((text, href))
                    if print_log:
                        print(f'Texto: {text}, Link: {href}')
                    if len(results) >= extract_amount:
                        break

            page += 1
            if len(links) == 0:  # Break the loop if there are no more links
                break

        except requests.HTTPError as e:
            print(f'Error accessing the page. Status code: {response.status_code}')
            print(f'Error message: {e}')
            break
        except Exception as e:
            print(f'An error occurred while processing the page: {e}')
            break

    return results


def get_episodes_watch_links_from_af(url: str, mal_id: int, print_log=False):
    '''
    Get all the episodes watch links in Anime Fire from an all-episodes Anime Fire URL.

    Args:
    - url: An Anime Fire all episodes URL in the generic format: https://animefire.plus/animes/anime-name-todos-os-episodios.
    - mal_id: The MAL ID of the anime.
    - print_log: Boolean indicating whether to print log messages.

    Returns:
    - List of dictionaries containing episode number, hyperlink to Anime Fire watch episode page, and MAL ID of the anime.
    '''
    if url is None:
        return None

    if print_log:
        print(f'Base URL: {url}')

    results: list[dict] = []
    try:
        base_url = url.split("-todos-os-episodios")[0]  # Remove a parte '-todos-os-episodios' da URL

        for i in range(1000):  # Assume que não haverá mais de 1000 episódios
            episode_url = f"{base_url}/{i}"
            episode_response = requests.get(episode_url)
            if episode_response.status_code == 404:
                if i == 0:
                    continue  # Se der erro no episódio 0, continue verificando
                else:
                    break  # Sai do loop quando não encontrar mais episódios

            soup = BeautifulSoup(episode_response.text, 'html.parser')
            links = soup.find_all('a')  # Verifica se há hyperlinks na página

            if not links:  # Se não houver hyperlinks, considera a página inválida
                if i == 0:
                    continue  # Se a página estiver vazia no episódio 0, continue verificando
                else:
                    break  # Sai do loop quando encontrar uma página sem hyperlinks

            if print_log:
                print(f'Watch link for episode {i}: {episode_url}')
            
            results.append({"mal_id": mal_id, "ep": i, "watch_link": episode_url})

    except Exception as e:
        print(f'An error occurred while processing the page: {e}')

    return results

def get_episodes_download_links_from_af(anime_name: str, mal_id: int, url=values.URL_AF_DOWNLOADS, print_log=False):
    '''
    Get all the episodes download links in Anime Fire from an anime name.

    Args:
    - anime_name: Name of the anime in the format: name-of-anime.
    - mal_id: The MAL ID of the anime.
    - url: Base URL for Anime Fire download links.
    - print_log: Boolean indicating whether to print log messages.

    Returns:
    - List of dictionaries containing episode number, download links for SD and HD versions, a boolean indicating if the episode is temporary, and MAL ID of the anime.
    '''
    results: list[dict] = []
    base_url = f"{url}{anime_name}/"
    if print_log:
        print(f'Base URL: {base_url}')
    
    try:
        for i in range(1000):  # Assume que não haverá mais de 1000 episódios
            episode_url = f"{base_url}{i}"
            episode_response = requests.get(episode_url)
            if episode_response.status_code == 404:
                if i == 0:
                    continue  # Se der erro no episódio 0, continue verificando
                else:
                    break  # Sai do loop quando não encontrar mais episódios
            
            soup = BeautifulSoup(episode_response.text, 'html.parser')
            
            links = soup.find_all('a')  # Find all anchor tags
            FILTER_STRINGS = values.URLS_AF_FILTER_DOWNLOADS_LINKS
            download_links = [link.get('href') for link in links if link.get('href') and any(fs in link.get('href') for fs in FILTER_STRINGS)]
            
            if not download_links and i != 0:
                break  # Sai do loop se não encontrar links após o episódio 0
            
            if download_links:
                episode_links = {'mal_id': mal_id, 'episode': i, 'sd': None, 'hd': None, 'temp': False}
                for link in download_links:
                    if "(SD)" in link:
                        episode_links['sd'] = link
                    elif "(HD)" in link:
                        episode_links['hd'] = link
                    if "mp4_temp" in link:
                        episode_links['temp'] = True
                results.append(episode_links)
                if print_log:
                    print(f"Download links for episode {i}: {episode_links}")
    
    except Exception as e:
        print(f'An error occurred while processing the page: {e}')

    return results

def get_anime_name_from_af_url(af_link: str, print_log = False):
    '''
    Extract the anime name from an Anime Fire link.

    Args:
    - af_url: A URL in the format: https://animefire.plus/animes/anime-name-todos-os-episodios.
    - print_log: Boolean indicating whether to print log messages.

    Returns:
    - The extracted anime name.
    '''
    try:
        # Remove the base URL and split by '/'
        parts = af_link.split('/')
        # Get the part containing the anime name and remove '-todos-os-episodios'
        anime_name = parts[-1].replace('-todos-os-episodios', '')
        if(print_log):
            print(f'Anime name: {anime_name}')
        return anime_name
    except Exception as e:
        print(f'An error occurred while extracting the anime name: {e}')
        return None



def search_anime_id_on_jikan_v4(anime_name: str, print_log=False) -> int:
    '''
    The Jikan_v4 API is used to search a anime in MyAnimeList (MAL).

    Args:
    - anime_name: String with the anime name to search.
    - print_log: Boolean indicating whether to print log messages.

    Returns:
    - Integer containing the anime id in MAL.
    '''
    BAD_ID = values.BAD_ID
    # Passo 1: Realizar uma pesquisa pelo nome do anime
    search_url = f"{values.URL_JIKAN_SEARCH}{anime_name}"
    response = requests.get(search_url)
    data = response.json()

    # Verificar se a pesquisa retornou resultados
    if 'data' in data and data['data']:
        # Pegar o ID do primeiro resultado da pesquisa
        anime_id = data['data'][0]['mal_id']
        if(print_log):
            print(anime_id)
        return anime_id
    else:
        print("Anime não encontrado.")
        return BAD_ID
    
def get_anime_resource_from_jikan_v4(anime_id: int, print_log=False):
    '''
    Get anime data from MAL through MyAnimeList (MAL) id by Jikan_v4 API

    Args:
    - anime_id: Integer containing the anime id get from MAL
    - print_log: Boolean indicating whether to print log messages.

    Returns:
    - Dictionary containing the anime data
    '''
    if anime_id == values.BAD_ID:
        return None

    search_url = f"{values.URL_JIKAN_SEARCH_BY_MALID}{anime_id}"
    response = requests.get(search_url)
    
    try:
        data = response.json()
    except ValueError:
        print("Error decoding JSON response")
        return None

    if 'data' in data:
        anime_data = data['data']
        if isinstance(anime_data, dict):  # Verifica se anime_data é um dicionário

            anime_dict = {
                'mal_id': anime_id,
                'title': anime_data.get('title', 'N/A'),
                'title_english': anime_data.get('title_english', 'N/A'),
                'title_japanese': anime_data.get('title_japanese', 'N/A'),
                'type': anime_data.get('type', 'N/A'),
                'episodes': anime_data.get('episodes', 'N/A'),
                'status': anime_data.get('status', 'N/A'),
                'airing': anime_data.get('airing', 'N/A'),
                'aired': anime_data.get('aired', {}).get('string', 'N/A'),
                'rating': anime_data.get('rating', 'N/A'),
                'duration': anime_data.get('duration', 'N/A'),
                'season': anime_data.get('season', 'N/A'),
                'year': anime_data.get('year', 'N/A'),
                'studios': ', '.join([studio['name'] for studio in anime_data.get('studios', [])]),
                'producers': ', '.join([producer['name'] for producer in anime_data.get('producers', [])]),
                'synopsis': anime_data.get('synopsis', 'N/A')
            }

            if print_log:
                print(anime_dict)

            return anime_dict
        else:
            print("Expected a dictionary for anime_data, got:", type(anime_data))
            return None
    else:
        print("Anime not found.")
        return None
    
def extract_releasing_animes_from_af(url_af=values.URL_AF_RELEASES, haders=values.HEADERS, extract_amount = 10, start_page = 1, print_log=False):
    '''
    Collect wacth and download links from Anime Fire and anime metadatas from MyAnimeList

    Args:
    - url_af: Url
    - haders: User agent
    - extract_amount: Number of links to extract.
    - start_page: Page number to start extraction from.
    - print_log: Boolean indicating whether to print log messages.

    Returns:
    - watch_links: Dictionary containing Anime Fire website links.

        Dictionary contains:
            'mal_id': ID of the anime on MAL.
            'ep': Episode number.
            'watch_link': Hyperlink to the episode viewing page on Anime Fire.

    - download_links: List of dictionaries containing Anime Fire download links.

        Each dictionary contains:
            'mal_id': ID of the anime on MAL.
            'episode': Episode number.
            'sd': Download link for the SD (standard definition) version of the episode.
            'hd': Download link for the HD (high definition) version of the episode.
            'temp': Boolean value indicating if the episode is temporary.

    - animes_metadata: List of dictionaries containing anime metadata from MyAnimeList (MAL) via the Jikan_v4 API.

        Each dictionary contains metadata fields including:
            'mal_id': ID of the anime on MAL.
            'title': Title of the anime.
            'title_english': English title of the anime.
            'title_japanese': Japanese title of the anime.
            'type': Type of the anime (e.g., TV, movie, OVA).
            'episodes': Number of episodes of the anime.
            'status': Airing status of the anime (e.g., "ongoing", "completed").
            'airing': Information about the current airing status of the anime.
            'aired': Air date of the anime.
            'rating': Rating of the anime.
            'duration': Duration of each episode of the anime.
            'season': Release season of the anime.
            'year': Release year of the anime.
            'studios': Studios responsible for producing the anime.
            'producers': Producers of the anime.
            'synopsis': Synopsis of the anime.
    '''
    anime_releases = get_title_and_hyperlinks_from_af(url_af=url_af, headers=haders, extract_amount=extract_amount, start_page=start_page, print_log=print_log) 
    # Etapa 2: Pesquisar cada anime na API do Jikan e obter o mal_id
    anime_ids = []
    watch_links = []
    download_links = []   
    for anime in anime_releases:
        anime_id = search_anime_id_on_jikan_v4(anime[0], print_log=print_log)
        if anime_id != values.BAD_ID:
            anime_ids.append(anime_id)
            watch_link = get_episodes_watch_links_from_af(anime[1], anime_id, print_log=print_log)
            watch_links.append(watch_link)
            anime_name = get_anime_name_from_af_url(anime[1], print_log=print_log)
            download_link = get_episodes_download_links_from_af(anime_name, anime_id,print_log=print_log)
            download_links.append(download_link)

    # Etapa 3: Obter detalhes do anime
    animes_metadata = []
    for anime_id in anime_ids:
        data = get_anime_resource_from_jikan_v4(anime_id, print_log=print_log)
        if data:
            animes_metadata.append(data)
    return watch_links, download_links, animes_metadata


def extract_custom_anime_from_af(anime_url_on_af: str, print_log= False):
    """
    Extrct a single anime from Anime Fire.

    Args:
     - anime_url_on_af: URL to the anime overview page on Anime Fire following the format: 
                        https://animefire.plus/animes/anime-name-todos-os-episodios.
     - print_log: Enable logging for debugging purposes.

    Returns:
     - A tuple of: watch_links, download_links, anime_metadata_from_mal
    """
    anime_name_romaji = anime_url_on_af.split('/')[-1].rstrip("-todos-os-episodios")
    anime_mal_id: int = search_anime_id_on_jikan_v4(anime_name=anime_name_romaji, print_log=print_log)
    if(anime_mal_id == values.BAD_ID):
        raise ValueError('Anime not found')
    anime_data = get_anime_resource_from_jikan_v4(anime_id=anime_mal_id, print_log=print_log)
    download_links = get_episodes_download_links_from_af(anime_name=anime_name_romaji, mal_id=anime_mal_id, print_log=print_log)
    watch_links = get_episodes_watch_links_from_af(url=anime_url_on_af, mal_id=anime_mal_id, print_log=print_log)
    return watch_links, download_links, anime_data





    
