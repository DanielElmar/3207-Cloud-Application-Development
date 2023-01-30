import {getScheduleShifts, getUnapprovedAvailabilities} from "$lib/api.js";


/** @type {import('./$types').PageServerLoad} */
export async function load({ locals, url }) {
    let urlParam = url.searchParams.get("weekCommencing");

    if (urlParam == null) {
        urlParam = new Date().toISOString();
    } else {
        urlParam = new Date(urlParam).toISOString();
    }

    let data = await getUnapprovedAvailabilities(locals.user.uuid, urlParam);

    if (data.error){
        return {approvals: [], error: data.error}
    }

    return data
}