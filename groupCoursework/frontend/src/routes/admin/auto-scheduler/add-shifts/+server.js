import { json } from "@sveltejs/kit";
import { createShift } from '$lib/api.js'

export async function POST({ request, locals }) {
	const data = await request.json();

	console.log(data);
    console.log(locals.user.uuid)

    let promises = [];
    for (const shift of data.shifts) {
        promises.push(createShift(locals.user.uuid, shift));
    }

    const values = await Promise.all(promises);

    console.log(values);

    let error = false;
    for (const value of values) {
        if (value?.error) error = true;
    }

	return json({error})
}
