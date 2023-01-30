# How to deploy

## Google App Engine Setup

1. Set up google app engine and create a new project.
1. Create a new app with region in the uk
1. Choose the standard environment
1. Set up gloud SDK (then gcloud init and sign in)

## Uploading to cloud
> Run all the next commands within the /frontend folder

1. Run `npm install` to install all the dependencies
1. Then run `npm run build` within (This builds the files for production)
1. Run `gcloud app deploy --version test` (Deploys to google app engine)

## To run locally
1. Run `npm install` to install all the dependencies
1. The run `npm run dev`
