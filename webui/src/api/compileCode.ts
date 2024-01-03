import {baseRequest} from "./baseRequest";
import {serverResponses} from "../types/ServerResponseEnum";

export const loginApi = async (code: string): Promise<{ success: boolean, message: string }> => {
    const result = await baseRequest("/compile", {code})
    if (result.status === serverResponses.success) {
        return {success: true, message: result.response.bytecode}
    } else {
        return {success: false, message: result.response}
    }
}