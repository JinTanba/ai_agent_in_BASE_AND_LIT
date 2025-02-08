code1 = """
if (typeof supabase === 'undefined') {
  const script = document.createElement('script');
  script.src = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js";
  script.onload = () => { console.log('Supabase library loaded'); };
  document.head.appendChild(script);
}"""

code2 = """
const SUPABASE_URL = 'https://lipbpiidmsjeuqemorzv.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxpcGJwaWlkbXNqZXVxZW1vcnp2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMTkyMTYwOSwiZXhwIjoyMDQ3NDk3NjA5fQ.OmyjfLjmZA_FDWO5R54G5-UFgtmGr64Nj4Wf_CCZ63o';
const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// (3) Define a function to upload a Blob to Supabase Storage:
async function uploadImage(blob, fileName) {
  const bucket = 'images'; // Make sure this bucket exists in Supabase Storage
  const { data, error } = await supabaseClient
    .storage
    .from(bucket)
    .upload(fileName, blob, {
      cacheControl: '3600',
      upsert: false,
    });
  if (error) {
    console.error(`Error uploading ${fileName}:`, error);
  } else {
    console.log(`Uploaded ${fileName}:`, data);
  }
}

function getUrlParam(url) {
  try {
    const { pathname } = new URL(url);
    // Split the pathname by '/' - the first element will be an empty string.
    const segments = pathname.split('/');
    return segments[1] || '';
  } catch (err) {
    console.error(`Invalid URL provided: ${url}`);
    return '';
  }
}


// (4) Get all images on the page and process them:
document.querySelectorAll('img').forEach(async (img) => {
  const src = img.src;
  if (!src) return; // Skip images without a source

  try {
    const response = await fetch(src);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const blob = await response.blob();

    // Create a unique file name (for example, using current timestamp and original filename)
    const fileName = `mdjn/${getUrlParam(src)}`

    await uploadImage(blob, fileName);
  } catch (err) {
    console.error(`Failed to process image ${src}:`, err);
  }
});
"""