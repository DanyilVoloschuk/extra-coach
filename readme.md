
# Nutrition Tracking Telegram Bot

A Telegram bot application that helps users track their nutritional intake and exercise activities. Built with FastAPI and SQLAlchemy.

## Features

- Track food intake with detailed nutritional information:
  - Calories
  - Proteins
  - Fats
  - Carbohydrates
- Log exercise activities and calories burned
- View daily nutrition summaries
- Admin interface for managing users and data

## Tech Stack

- Python 3.11
- FastAPI - Web framework
- SQLAlchemy - Database ORM
- SQLAdmin - Admin interface
- Alembic - Database migrations
- Telegram Bot API

## Prerequisites

- Python 3.11.5
- Virtual environment

## Installation

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies
4. Set up and fill environment variables `cp .env.txt .env`
5. Migrate db `alembic upgrade head`


## Running the Application

Start the FastAPI server:
`python app.py`

## Admin Interface

Access the admin interface at `/admin` with these default credentials:
- Username: admin
- Password: admin

## API Endpoints

- `POST /webhook` - Telegram webhook endpoint for handling bot messages
- `GET /` - Health check endpoint

## Data Models

- User - Stores user information
- UserChat - Manages Telegram chat sessions
- NutritionalData - Stores food and exercise entries

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

### Key License Terms:

- You may copy, distribute and modify the software.
- You must include the original source code when you distribute the software.
- All modifications and derivative works must also be licensed under GPLv3.
- Changes made to the code must be documented.
- No additional restrictions - you cannot restrict anyone else from making copies of your version.

For the full license text, see the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
