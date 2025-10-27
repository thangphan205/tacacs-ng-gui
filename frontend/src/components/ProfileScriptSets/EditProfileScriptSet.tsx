import {
  Button,
  ButtonGroup,
  DialogActionTrigger,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FaExchangeAlt } from "react-icons/fa"

import { type ApiError, type ProfileScriptSetPublic, ProfilescriptsetsService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

interface EditProfileScriptSetProps {
  profilescriptset: ProfileScriptSetPublic
}

interface ProfileScriptSetUpdateForm {
  key: string;
  value: string;
  description?: (string | null);
  profilescript_id: string;
}

const EditProfileScriptSet = ({ profilescriptset }: EditProfileScriptSetProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ProfileScriptSetUpdateForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      ...profilescriptset,
      description: profilescriptset.description ?? undefined,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: ProfileScriptSetUpdateForm) =>
      ProfilescriptsetsService.updateProfilescriptset({ id: profilescriptset.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("ProfileScriptSet updated successfully.")
      reset()
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["profilescriptsets"] })
    },
  })

  const onSubmit: SubmitHandler<ProfileScriptSetUpdateForm> = async (data) => {
    mutation.mutate(data)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button variant="ghost">
          <FaExchangeAlt fontSize="16px" />
          Edit ProfileScriptSet
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Edit ProfileScriptSet</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>Update the item details below.</Text>
            <VStack gap={4}>
              <Field
                required
                invalid={!!errors.key}
                errorText={errors.key?.message}
                label="key"
              >
                <Input
                  {...register("key", {
                    required: "key is required",
                  })}
                  placeholder="key"
                  type="text"
                />
              </Field>
              <Field
                required
                invalid={!!errors.value}
                errorText={errors.value?.message}
                label="value"
              >
                <Input
                  {...register("value", {
                    required: "value is required",
                  })}
                  placeholder="value"
                  type="text"
                />
              </Field>
              <Field
                required
                invalid={!!errors.profilescript_id}
                errorText={errors.profilescript_id?.message}
                label="profilescript_id"
              >
                <Input
                  {...register("profilescript_id", {
                    required: "profilescript_id is required",
                  })}
                  placeholder="profilescript_id"
                  type="text"
                />
              </Field>
              <Field
                invalid={!!errors.description}
                errorText={errors.description?.message}
                label="Description"
              >
                <Input
                  {...register("description")}
                  placeholder="Description"
                  type="text"
                />
              </Field>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <ButtonGroup>
              <DialogActionTrigger asChild>
                <Button
                  variant="subtle"
                  colorPalette="gray"
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
              </DialogActionTrigger>
              <Button variant="solid" type="submit" loading={isSubmitting}>
                Save
              </Button>
            </ButtonGroup>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default EditProfileScriptSet
